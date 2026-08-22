"""Persistence roots for Takdora's owner and workspace domain."""

from __future__ import annotations

from datetime import UTC, datetime

import reflex as rx
from sqlalchemy import UniqueConstraint
from sqlmodel import Field


class FoundationProbe(rx.Model, table=True):
    """A non-sensitive row written by the readiness diagnostic control."""

    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class OwnerAccount(rx.Model, table=True):
    """A password-authenticated owner; password material is always one-way derived."""

    __table_args__ = (UniqueConstraint("normalized_email", name="uq_owner_normalized_email"),)

    normalized_email: str = Field(index=True)
    password_digest: str
    password_salt: str
    email_verified_at: datetime | None = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class AuthSession(rx.Model, table=True):
    """Server-side session record; the browser receives only its opaque raw token."""

    session_digest: str = Field(index=True, unique=True)
    owner_id: int = Field(foreign_key="owneraccount.id", index=True)
    expires_at: datetime
    revoked_at: datetime | None = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class EmailVerificationToken(rx.Model, table=True):
    """One-time token proving the owner controls their email address."""

    token_digest: str = Field(index=True, unique=True)
    owner_id: int = Field(foreign_key="owneraccount.id", index=True)
    expires_at: datetime
    consumed_at: datetime | None = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class PasswordResetToken(rx.Model, table=True):
    """One-time expiring credential reset token stored only as a digest."""

    token_digest: str = Field(index=True, unique=True)
    owner_id: int = Field(foreign_key="owneraccount.id", index=True)
    expires_at: datetime
    consumed_at: datetime | None = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class Business(rx.Model, table=True):
    """The single tenant root owned by one account in Takdora v1."""

    __table_args__ = (UniqueConstraint("creating_owner_id", name="uq_business_creating_owner"),)

    creating_owner_id: int = Field(foreign_key="owneraccount.id", index=True)
    name: str = Field(default="")
    slug: str = Field(default="", index=True)
    is_active: bool = Field(default=True, index=True)
    deletion_requested_at: datetime | None = Field(default=None)
    purge_after: datetime | None = Field(default=None, index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class BusinessMembership(rx.Model, table=True):
    """Future-compatible authority record; v1 only creates the owner membership."""

    __table_args__ = (
        UniqueConstraint("business_id", "owner_id", name="uq_business_owner_membership"),
        UniqueConstraint("owner_id", name="uq_one_workspace_per_owner"),
    )

    business_id: int = Field(foreign_key="business.id", index=True)
    owner_id: int = Field(foreign_key="owneraccount.id", index=True)
    role: str = Field(default="owner")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


def record_probe() -> FoundationProbe:
    """Persist then retrieve a diagnostic row using Reflex's configured database session."""
    with rx.session() as session:
        probe = FoundationProbe()
        session.add(probe)
        session.commit()
        session.refresh(probe)
        return probe
