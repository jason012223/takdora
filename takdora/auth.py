"""Server-side owner authentication primitives and bounded Reflex state."""

from __future__ import annotations

import hashlib
import hmac
import re
import secrets
from datetime import UTC, datetime, timedelta

import reflex as rx
from sqlmodel import select

from takdora.models import AuthSession, OwnerAccount

MIN_PASSWORD_LENGTH = 12
SESSION_TTL = timedelta(days=14)
_EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class AuthenticationError(ValueError):
    """Raised for a bounded invalid login response."""


class SessionCredentialError(ValueError):
    """Raised for a malformed browser session credential."""


def normalize_email(email: str) -> str:
    """Return the canonical account address without accepting malformed values."""
    normalized = email.strip().casefold()
    if not _EMAIL_PATTERN.fullmatch(normalized):
        raise AuthenticationError("Enter a valid email address.")
    return normalized


def validate_password(password: str) -> None:
    """Keep the password policy concise and enforce it solely on the server."""
    if len(password) < MIN_PASSWORD_LENGTH:
        raise AuthenticationError(
            f"Use at least {MIN_PASSWORD_LENGTH} characters for your password."
        )


def create_password_digest(password: str) -> tuple[str, str]:
    """Derive a one-way scrypt digest using a new random salt per account."""
    validate_password(password)
    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(password.encode(), salt=salt, n=2**14, r=8, p=1).hex()
    return digest, salt.hex()


def verify_password(password: str, password_digest: str, password_salt: str) -> bool:
    """Compare a supplied password with a stored digest in constant time."""
    try:
        candidate = hashlib.scrypt(
            password.encode(), salt=bytes.fromhex(password_salt), n=2**14, r=8, p=1
        ).hex()
    except (TypeError, ValueError):
        return False
    return hmac.compare_digest(candidate, password_digest)


def digest_token(token: str, *, minimum_length: int = 32) -> str:
    """Digest an opaque browser/token credential without logging its raw value."""
    if len(token) < minimum_length or not re.fullmatch(r"[A-Za-z0-9_-]+", token):
        raise SessionCredentialError("Invalid session credential.")
    return hashlib.sha256(token.encode()).hexdigest()


def create_session_credential() -> tuple[str, str]:
    """Return an opaque raw token and its server-persistable digest."""
    raw = secrets.token_urlsafe(32)
    return raw, digest_token(raw)


def verify_session_credential(
    raw_credential: str, stored_digest: str, expires_at: datetime, *, revoked: bool = False
) -> bool:
    """Verify a session without treating a browser value as authorization by itself."""
    try:
        credential_digest = digest_token(raw_credential)
    except SessionCredentialError:
        return False
    return (
        not revoked
        and expires_at > datetime.now(UTC)
        and hmac.compare_digest(credential_digest, stored_digest)
    )


def create_owner(email: str, password: str) -> OwnerAccount:
    """Persist one locally authenticated owner, never a recoverable password."""
    normalized_email = normalize_email(email)
    password_digest, password_salt = create_password_digest(password)
    with rx.session() as session:
        existing = session.exec(
            select(OwnerAccount).where(OwnerAccount.normalized_email == normalized_email)
        ).first()
        if existing:
            raise AuthenticationError("An account already exists for that email address.")
        owner = OwnerAccount(
            normalized_email=normalized_email,
            password_digest=password_digest,
            password_salt=password_salt,
        )
        session.add(owner)
        session.commit()
        session.refresh(owner)
        return owner


def authenticate_owner(email: str, password: str) -> OwnerAccount:
    """Return an owner only after constant-time credential validation."""
    normalized_email = normalize_email(email)
    with rx.session() as session:
        owner = session.exec(
            select(OwnerAccount).where(OwnerAccount.normalized_email == normalized_email)
        ).first()
        if owner is None or not verify_password(
            password, owner.password_digest, owner.password_salt
        ):
            raise AuthenticationError("Email or password is incorrect.")
        return owner


def issue_session(owner_id: int) -> str:
    """Persist a digest-only authenticated session and return its browser credential."""
    raw, session_digest = create_session_credential()
    with rx.session() as session:
        session.add(
            AuthSession(
                owner_id=owner_id,
                session_digest=session_digest,
                expires_at=datetime.now(UTC) + SESSION_TTL,
            )
        )
        session.commit()
    return raw


def resolve_session_owner(raw_credential: str) -> OwnerAccount | None:
    """Resolve an active server-side session, returning no detail for invalid values."""
    try:
        credential_digest = digest_token(raw_credential)
    except SessionCredentialError:
        return None
    with rx.session() as session:
        auth_session = session.exec(
            select(AuthSession).where(AuthSession.session_digest == credential_digest)
        ).first()
        if auth_session is None or not verify_session_credential(
            raw_credential,
            auth_session.session_digest,
            auth_session.expires_at,
            revoked=auth_session.revoked_at is not None,
        ):
            return None
        return session.get(OwnerAccount, auth_session.owner_id)


def revoke_session(raw_credential: str) -> None:
    """Revoke the current opaque credential if it resolves to a server record."""
    try:
        credential_digest = digest_token(raw_credential)
    except SessionCredentialError:
        return
    with rx.session() as session:
        auth_session = session.exec(
            select(AuthSession).where(AuthSession.session_digest == credential_digest)
        ).first()
        if auth_session is not None:
            auth_session.revoked_at = datetime.now(UTC)
            session.add(auth_session)
            session.commit()


class AuthState(rx.State):
    """Browser-safe state: only the opaque session cookie crosses the boundary."""

    session_credential: str = rx.Cookie(name="takdora_session", path="/", max_age=1209600)
    email: str = ""
    password: str = ""
    feedback_message: str = ""

    @property
    def current_owner(self) -> OwnerAccount | None:
        return resolve_session_owner(self.session_credential)

    @property
    def is_authenticated(self) -> bool:
        return self.current_owner is not None

    def require_owner(self) -> OwnerAccount:
        """Guard private events using the server-side credential resolution."""
        owner = self.current_owner
        if owner is None:
            raise AuthenticationError("Please sign in to continue.")
        return owner

    def register(self) -> rx.event.EventSpec | None:
        try:
            owner = create_owner(self.email, self.password)
        except AuthenticationError as error:
            self.feedback_message = str(error)
            return None
        self.session_credential = issue_session(owner.id or 0)
        self.password = ""
        return rx.redirect("/owner")

    def sign_in(self) -> rx.event.EventSpec | None:
        try:
            owner = authenticate_owner(self.email, self.password)
        except AuthenticationError:
            self.feedback_message = "Email or password is incorrect."
            return None
        self.session_credential = issue_session(owner.id or 0)
        self.password = ""
        return rx.redirect("/owner")

    def sign_out(self) -> rx.event.EventSpec:
        revoke_session(self.session_credential)
        self.session_credential = ""
        self.feedback_message = ""
        return rx.redirect("/sign-in")
