"""Validated, tenant-bound business setup and future publication readiness."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import UTC, datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import reflex as rx
from sqlmodel import select

from takdora.models import Business, BusinessSlugRedirect, OwnerAccount
from takdora.tenancy import WorkspaceAccessError, get_workspace_for_owner, require_owner

_SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_COLOR_PATTERN = re.compile(r"^#[0-9A-Fa-f]{6}$")


@dataclass(frozen=True)
class BusinessProfileInput:
    name: str
    contact_email: str = ""
    contact_phone: str = ""
    address: str = ""
    slug: str = ""
    timezone: str = "Asia/Manila"
    currency: str = "PHP"
    logo_url: str | None = None
    accent_color: str | None = None
    invoice_identity: str = ""


@dataclass(frozen=True)
class Branding:
    logo_label: str
    accent_color: str


@dataclass(frozen=True)
class PublishReadiness:
    """One shared truth source for the review screen and future public route."""

    ready: bool
    missing_required: tuple[str, ...]


@dataclass(frozen=True)
class SlugChange:
    """Canonical address plus an optional prior address to retain as a redirect."""

    canonical_slug: str
    redirect_from: str | None


def normalize_slug(value: str) -> str:
    """Create a short, URL-safe public identifier from an editable business name."""
    if not value.strip() or re.search(r"[!/:?@]", value):
        raise ValueError("Use letters, numbers, and single hyphens for the public address.")
    normalized = re.sub(r"[^a-z0-9]+", "-", value.casefold().strip()).strip("-")
    normalized = re.sub(r"-{2,}", "-", normalized)
    if not normalized or not _SLUG_PATTERN.fullmatch(normalized):
        raise ValueError("Use letters, numbers, and single hyphens for the public address.")
    return normalized


def default_branding(logo_url: str | None, accent_color: str | None) -> Branding:
    """Keep an unfinished workspace polished without requiring design choices."""
    return Branding(logo_label=logo_url or "Takdora", accent_color=accent_color or "#C65D21")


def validate_profile(profile: BusinessProfileInput) -> BusinessProfileInput:
    """Validate persisted setup values on the server before an owner can save them."""
    name = profile.name.strip()
    if not name:
        raise ValueError("Business name is required.")
    slug = normalize_slug(profile.slug or name)
    try:
        ZoneInfo(profile.timezone)
    except ZoneInfoNotFoundError as error:
        raise ValueError("Choose a valid IANA time zone.") from error
    if profile.currency != "PHP":
        raise ValueError("PHP is the supported currency for this Philippines-first release.")
    if profile.logo_url and not profile.logo_url.startswith("https://"):
        raise ValueError("Logo URL must use HTTPS.")
    if profile.accent_color and not _COLOR_PATTERN.fullmatch(profile.accent_color):
        raise ValueError("Accent color must be a six-digit hex color.")
    return BusinessProfileInput(
        name=name,
        contact_email=profile.contact_email.strip(),
        contact_phone=profile.contact_phone.strip(),
        address=profile.address.strip(),
        slug=slug,
        timezone=profile.timezone,
        currency=profile.currency,
        logo_url=profile.logo_url,
        accent_color=profile.accent_color,
        invoice_identity=profile.invoice_identity.strip(),
    )


def evaluate_publish_readiness(
    *,
    email_verified: bool,
    business_name: str,
    slug: str,
    has_active_service: bool,
    has_working_hours: bool,
) -> PublishReadiness:
    """Report the exact requirements honestly before a public page can be published."""
    missing: list[str] = []
    if not email_verified:
        missing.append("Verify email")
    if not business_name.strip():
        missing.append("Add business name")
    try:
        normalize_slug(slug)
    except ValueError:
        missing.append("Choose a public address")
    if not has_active_service:
        missing.append("Add a service")
    if not has_working_hours:
        missing.append("Set working hours")
    return PublishReadiness(ready=not missing, missing_required=tuple(missing))


def evaluate_publish_readiness_for_owner(owner: OwnerAccount | None) -> PublishReadiness:
    """Read live catalog and schedule adapters instead of trusting onboarding browser state."""
    from takdora.availability import has_weekly_working_hours_for_business
    from takdora.services import active_service_present_for_business

    authorized_owner = require_owner(owner)
    business = get_workspace_for_owner(authorized_owner)
    if business is None:
        raise WorkspaceAccessError("Workspace not found.")
    return evaluate_publish_readiness(
        email_verified=authorized_owner.email_verified_at is not None,
        business_name=business.name,
        slug=business.slug,
        has_active_service=active_service_present_for_business(business.id or 0),
        has_working_hours=has_weekly_working_hours_for_business(business.id or 0),
    )


def slug_change_plan(current_slug: str, next_slug: str, *, is_published: bool) -> SlugChange:
    """Plan a canonical slug update without dropping a shared published address."""
    canonical_slug = normalize_slug(next_slug)
    previous_slug = normalize_slug(current_slug) if current_slug else ""
    return SlugChange(
        canonical_slug=canonical_slug,
        redirect_from=previous_slug if is_published and previous_slug != canonical_slug else None,
    )


def save_profile(owner: OwnerAccount | None, profile: BusinessProfileInput) -> Business:
    """Autosave a validated profile to the one server-authorized workspace."""
    authorized_owner = require_owner(owner)
    validated = validate_profile(profile)
    business = get_workspace_for_owner(authorized_owner)
    if business is None:
        raise WorkspaceAccessError("Workspace not found.")
    with rx.session() as session:
        stored = session.get(Business, business.id)
        if stored is None or stored.creating_owner_id != authorized_owner.id:
            raise WorkspaceAccessError("Workspace not found.")
        for field_name, value in validated.__dict__.items():
            setattr(stored, field_name, value)
        session.add(stored)
        session.commit()
        session.refresh(stored)
        return stored


def change_business_slug(
    owner: OwnerAccount | None, next_slug: str, *, is_published: bool
) -> Business:
    """Atomically reserve a published prior address before moving the canonical slug."""
    authorized_owner = require_owner(owner)
    with rx.session() as session:
        business = session.exec(
            select(Business)
            .where(Business.creating_owner_id == authorized_owner.id)
            .with_for_update()
        ).first()
        if business is None:
            raise WorkspaceAccessError("Workspace not found.")
        change = slug_change_plan(business.slug, next_slug, is_published=is_published)
        existing_business = session.exec(
            select(Business).where(
                Business.slug == change.canonical_slug, Business.id != business.id
            )
        ).first()
        existing_redirect = session.exec(
            select(BusinessSlugRedirect).where(BusinessSlugRedirect.slug == change.canonical_slug)
        ).first()
        if existing_business is not None or existing_redirect is not None:
            raise ValueError("That public address is already in use.")
        if change.redirect_from:
            session.add(
                BusinessSlugRedirect(business_id=business.id or 0, slug=change.redirect_from)
            )
        business.slug = change.canonical_slug
        session.add(business)
        session.commit()
        session.refresh(business)
        return business


def publish_business(owner: OwnerAccount | None) -> Business:
    """Expose a workspace only after rechecking readiness on the server."""
    authorized_owner = require_owner(owner)
    readiness = evaluate_publish_readiness_for_owner(authorized_owner)
    if not readiness.ready:
        raise ValueError(
            "Complete setup before publishing: " + ", ".join(readiness.missing_required)
        )
    with rx.session() as session:
        business = session.exec(
            select(Business)
            .where(Business.creating_owner_id == authorized_owner.id)
            .with_for_update()
        ).first()
        if business is None or not business.is_active or business.deletion_requested_at is not None:
            raise WorkspaceAccessError("Workspace cannot be published.")
        business.published_at = datetime.now(UTC)
        session.add(business)
        session.commit()
        session.refresh(business)
        return business
