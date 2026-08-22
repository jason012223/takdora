"""Persistence roots for Takdora's owner and workspace domain."""

from __future__ import annotations

from datetime import UTC, date, datetime, time
from decimal import Decimal

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
    contact_email: str = Field(default="")
    contact_phone: str = Field(default="")
    address: str = Field(default="")
    timezone: str = Field(default="Asia/Manila")
    currency: str = Field(default="PHP")
    logo_url: str | None = Field(default=None)
    accent_color: str | None = Field(default=None)
    invoice_identity: str = Field(default="")
    is_active: bool = Field(default=True, index=True)
    published_at: datetime | None = Field(default=None, index=True)
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


class BusinessSlugRedirect(rx.Model, table=True):
    """Durable prior public addresses to be resolved by the future public router."""

    __table_args__ = (UniqueConstraint("slug", name="uq_business_slug_redirect"),)

    business_id: int = Field(foreign_key="business.id", index=True)
    slug: str = Field(index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class BusinessService(rx.Model, table=True):
    """A history-preserving, fixed-duration service offered by one business."""

    business_id: int = Field(foreign_key="business.id", index=True)
    name: str = Field(max_length=120)
    description: str | None = Field(default=None, max_length=1000)
    fixed_duration_minutes: int
    price: Decimal | None = Field(default=None, max_digits=12, decimal_places=2)
    is_active: bool = Field(default=True, index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class WeeklyAvailabilityBlock(rx.Model, table=True):
    """A recurring local-time weekly policy block, never an appointment timestamp."""

    business_id: int = Field(foreign_key="business.id", index=True)
    weekday: int = Field(index=True)
    start_time: time
    end_time: time
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class BookingRules(rx.Model, table=True):
    """One explicit scheduling policy per business, seeded with low-friction defaults."""

    __table_args__ = (UniqueConstraint("business_id", name="uq_booking_rules_business"),)

    business_id: int = Field(foreign_key="business.id", index=True)
    slot_interval_minutes: int = Field(default=30)
    minimum_lead_minutes: int = Field(default=60)
    booking_horizon_days: int = Field(default=30)
    buffer_minutes: int = Field(default=0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class DateClosure(rx.Model, table=True):
    """A complete local business date that cannot be booked; reasons are deliberately absent."""

    __table_args__ = (UniqueConstraint("business_id", "local_date", name="uq_date_closure"),)

    business_id: int = Field(foreign_key="business.id", index=True)
    local_date: date = Field(index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class Booking(rx.Model, table=True):
    """A customer-safe appointment snapshot; all instants are stored as UTC."""

    __table_args__ = (UniqueConstraint("business_id", "idempotency_key", name="uq_booking_key"),)

    business_id: int = Field(foreign_key="business.id", index=True)
    service_id: int = Field(foreign_key="businessservice.id", index=True)
    status: str = Field(default="scheduled", index=True)
    customer_name: str
    customer_email: str
    customer_phone: str | None = Field(default=None)
    customer_note: str | None = Field(default=None)
    starts_at: datetime
    ends_at: datetime
    business_timezone: str
    idempotency_key: str = Field(max_length=96)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class BookingConfirmationOutbox(rx.Model, table=True):
    """One durable, post-commit confirmation delivery record per booking."""

    __table_args__ = (UniqueConstraint("booking_id", name="uq_booking_confirmation_booking"),)

    business_id: int = Field(foreign_key="business.id", index=True)
    booking_id: int = Field(foreign_key="booking.id", index=True)
    recipient_email: str
    delivery_status: str = Field(default="pending", index=True)
    attempts: int = Field(default=0)
    last_error: str | None = Field(default=None, max_length=240)
    sent_at: datetime | None = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class BookingOperationAudit(rx.Model, table=True):
    """Immutable internal evidence for a deliberate owner booking change."""

    business_id: int = Field(foreign_key="business.id", index=True)
    booking_id: int = Field(foreign_key="booking.id", index=True)
    actor_owner_id: int = Field(foreign_key="owneraccount.id", index=True)
    action: str = Field(max_length=32)
    prior_status: str = Field(max_length=16)
    new_status: str = Field(max_length=16)
    audit_details: str = Field(default="", max_length=1000)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class BookingChangeOutbox(rx.Model, table=True):
    """A post-commit customer update, unique per booking action type."""

    __table_args__ = (
        UniqueConstraint("booking_id", "message_type", name="uq_booking_change_message"),
    )

    business_id: int = Field(foreign_key="business.id", index=True)
    booking_id: int = Field(foreign_key="booking.id", index=True)
    message_type: str = Field(max_length=32)
    recipient_email: str
    customer_message: str | None = Field(default=None, max_length=500)
    delivery_status: str = Field(default="pending", index=True)
    attempts: int = Field(default=0)
    last_error: str | None = Field(default=None, max_length=240)
    sent_at: datetime | None = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


def record_probe() -> FoundationProbe:
    """Persist then retrieve a diagnostic row using Reflex's configured database session."""
    with rx.session() as session:
        probe = FoundationProbe()
        session.add(probe)
        session.commit()
        session.refresh(probe)
        return probe
