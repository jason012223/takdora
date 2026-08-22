"""Validated, tenant-bound business setup and future publication readiness."""

from __future__ import annotations

import re
from dataclasses import dataclass
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import reflex as rx

from takdora.models import Business, OwnerAccount
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
