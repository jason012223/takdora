"""Server-side owner authentication primitives and bounded Reflex state."""

from __future__ import annotations

import hashlib
import hmac
import re
import secrets
from datetime import UTC, datetime, timedelta
from urllib.parse import urlencode, urlsplit

import reflex as rx
from sqlmodel import select

from takdora.config import get_settings
from takdora.mailer import MailDeliveryError, Mailer
from takdora.models import AuthSession, EmailVerificationToken, OwnerAccount, PasswordResetToken

MIN_PASSWORD_LENGTH = 12
SESSION_TTL = timedelta(days=14)
RESET_TTL = timedelta(minutes=30)
_EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _as_utc(value: datetime) -> datetime:
    """Treat database timestamps without an offset as UTC before comparison."""
    return value.replace(tzinfo=UTC) if value.tzinfo is None else value.astimezone(UTC)


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


def create_one_time_token() -> tuple[str, str]:
    """Return a random one-time token and its digest for persistence."""
    raw = secrets.token_urlsafe(32)
    return raw, digest_token(raw)


def reset_token_is_usable(
    raw_token: str, stored_digest: str, expires_at: datetime, *, consumed_at: datetime | None
) -> bool:
    """Check reset token integrity, consumption state, and expiry without side effects."""
    try:
        token_digest = digest_token(raw_token)
    except SessionCredentialError:
        return False
    return (
        consumed_at is None
        and _as_utc(expires_at) > datetime.now(UTC)
        and hmac.compare_digest(token_digest, stored_digest)
    )


def build_public_token_url(origin: str, path: str, raw_token: str) -> str:
    """Build an absolute one-time URL from a validated public origin."""
    parsed = urlsplit(origin)
    if parsed.scheme != "https" or not parsed.netloc or parsed.path not in ("", "/"):
        raise AuthenticationError("A secure public application origin is required.")
    return f"{origin.rstrip('/')}{path}?{urlencode({'token': raw_token})}"


def issue_password_reset(owner_id: int) -> str:
    """Invalidate prior reset records and persist one fresh 30-minute credential."""
    raw_token, token_digest = create_one_time_token()
    with rx.session() as session:
        prior_tokens = session.exec(
            select(PasswordResetToken).where(
                PasswordResetToken.owner_id == owner_id,
                PasswordResetToken.consumed_at.is_(None),
            )
        ).all()
        now = datetime.now(UTC)
        for prior_token in prior_tokens:
            prior_token.consumed_at = now
            session.add(prior_token)
        session.add(
            PasswordResetToken(
                owner_id=owner_id,
                token_digest=token_digest,
                expires_at=now + RESET_TTL,
            )
        )
        session.commit()
    return raw_token


def issue_email_verification(owner_id: int) -> str:
    """Persist one 30-minute verification credential after the owner account commit."""
    raw_token, token_digest = create_one_time_token()
    with rx.session() as session:
        session.add(
            EmailVerificationToken(
                owner_id=owner_id,
                token_digest=token_digest,
                expires_at=datetime.now(UTC) + RESET_TTL,
            )
        )
        session.commit()
    return raw_token


def send_verification_email(owner: OwnerAccount, *, mailer: Mailer | None = None) -> None:
    """Send an email-verification link only after its token has committed."""
    raw_token = issue_email_verification(owner.id or 0)
    settings = get_settings()
    sender = mailer or Mailer(settings)
    sender.send_verification(
        owner.normalized_email,
        build_public_token_url(settings.public_app_origin, "/verify-email", raw_token),
    )


def request_password_reset(email: str, *, mailer: Mailer | None = None) -> None:
    """Request reset mail without disclosing whether the account exists."""
    try:
        normalized_email = normalize_email(email)
    except AuthenticationError:
        return
    with rx.session() as session:
        owner = session.exec(
            select(OwnerAccount).where(OwnerAccount.normalized_email == normalized_email)
        ).first()
    if owner is None:
        return
    raw_token = issue_password_reset(owner.id or 0)
    settings = get_settings()
    sender = mailer or Mailer(settings)
    sender.send_password_reset(
        owner.normalized_email,
        build_public_token_url(settings.public_app_origin, "/reset-password", raw_token),
    )


def consume_password_reset(raw_token: str, new_password: str) -> bool:
    """Atomically consume a valid token, update credentials, and revoke all sessions."""
    validate_password(new_password)
    try:
        token_digest = digest_token(raw_token)
    except SessionCredentialError:
        return False
    with rx.session() as session:
        reset_record = session.exec(
            select(PasswordResetToken).where(PasswordResetToken.token_digest == token_digest)
        ).first()
        if reset_record is None or not reset_token_is_usable(
            raw_token,
            reset_record.token_digest,
            reset_record.expires_at,
            consumed_at=reset_record.consumed_at,
        ):
            return False
        owner = session.get(OwnerAccount, reset_record.owner_id)
        if owner is None:
            return False
        password_digest, password_salt = create_password_digest(new_password)
        now = datetime.now(UTC)
        owner.password_digest = password_digest
        owner.password_salt = password_salt
        reset_record.consumed_at = now
        active_sessions = session.exec(
            select(AuthSession).where(
                AuthSession.owner_id == owner.id,
                AuthSession.revoked_at.is_(None),
            )
        ).all()
        for auth_session in active_sessions:
            auth_session.revoked_at = now
            session.add(auth_session)
        session.add(owner)
        session.add(reset_record)
        session.commit()
    return True


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
        and _as_utc(expires_at) > datetime.now(UTC)
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
    reset_token: str = ""
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

    def request_reset(self) -> None:
        """Keep the response neutral so this event cannot enumerate accounts."""
        try:
            request_password_reset(self.email)
        except MailDeliveryError:
            self.feedback_message = "We could not send that email yet. Please try again shortly."
        else:
            self.feedback_message = "If an account exists, we sent reset instructions."

    def reset_password(self) -> rx.event.EventSpec | None:
        if consume_password_reset(self.reset_token, self.password):
            self.password = ""
            self.reset_token = ""
            return rx.redirect("/sign-in")
        self.feedback_message = "That reset link is invalid or has expired. Request a new one."
        return None

    def capture_reset_token(self) -> None:
        """Read the browser URL token only to submit it to the server-side consumer."""
        query = self.router_data.get("query", {})
        token = query.get("token", "") if isinstance(query, dict) else ""
        self.reset_token = token if isinstance(token, str) else ""
