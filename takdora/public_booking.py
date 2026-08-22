"""Anonymous read boundary for a published business and its advisory booking slots."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import reflex as rx
from sqlmodel import select

from takdora.availability import AvailabilitySlot
from takdora.models import Business, BusinessService, BusinessSlugRedirect
from takdora.services import CustomerService, customer_service_projection


class PublicBookingUnavailable(ValueError):
    """Deliberately bounded result for all unavailable public addresses."""


@dataclass(frozen=True)
class PublicBusiness:
    slug: str
    name: str
    contact_email: str
    contact_phone: str
    address: str
    timezone: str
    logo_url: str | None
    accent_color: str | None
    services: tuple[CustomerService, ...]


@dataclass(frozen=True)
class PublicResolution:
    business: PublicBusiness | None = None
    redirect_slug: str | None = None


def valid_browser_timezone(value: str, *, fallback: str) -> tuple[str, bool]:
    """Accept a browser zone as display preference only, never booking authority."""
    try:
        ZoneInfo(value)
    except (TypeError, ZoneInfoNotFoundError):
        return fallback, False
    return value, True


def format_slot_for_timezone(slot: AvailabilitySlot, timezone_name: str) -> tuple[str, str]:
    zone = ZoneInfo(timezone_name)
    local = slot.start_at_utc.astimezone(zone)
    return local.strftime("%a, %b %d · %I:%M %p").replace(" 0", " "), zone.key


def resolve_public_business(slug: str) -> PublicResolution:
    """Resolve only a currently published, active, non-deleting workspace."""
    with rx.session() as session:
        business = session.exec(select(Business).where(Business.slug == slug)).first()
        if business is not None and _is_publicly_available(business):
            services = session.exec(
                select(BusinessService)
                .where(
                    BusinessService.business_id == business.id,
                    BusinessService.is_active.is_(True),
                )
                .order_by(BusinessService.name)
            ).all()
            return PublicResolution(
                business=PublicBusiness(
                    slug=business.slug,
                    name=business.name,
                    contact_email=business.contact_email,
                    contact_phone=business.contact_phone,
                    address=business.address,
                    timezone=business.timezone,
                    logo_url=business.logo_url,
                    accent_color=business.accent_color,
                    services=tuple(
                        customer_service_projection(item, currency=business.currency)
                        for item in services
                    ),
                )
            )
        redirect = session.exec(
            select(BusinessSlugRedirect).where(BusinessSlugRedirect.slug == slug)
        ).first()
        if redirect is not None:
            target = session.get(Business, redirect.business_id)
            if target is not None and _is_publicly_available(target):
                return PublicResolution(redirect_slug=target.slug)
    return PublicResolution()


def _is_publicly_available(business: Business) -> bool:
    return bool(
        business.published_at is not None
        and business.is_active
        and business.deletion_requested_at is None
    )


def public_slots_for_day(
    slug: str,
    service_id: int,
    visitor_day: date,
    browser_timezone: str,
    *,
    now: datetime | None = None,
) -> tuple[AvailabilitySlot, ...]:
    """Project authoritative UTC slots into a visitor-local day without new rules."""
    resolution = resolve_public_business(slug)
    if resolution.business is None:
        raise PublicBookingUnavailable("This booking page is unavailable.")
    business = resolution.business
    zone_name, _valid = valid_browser_timezone(browser_timezone, fallback=business.timezone)
    visitor_zone = ZoneInfo(zone_name)
    with rx.session() as session:
        stored_business = session.exec(select(Business).where(Business.slug == slug)).first()
        service = session.get(BusinessService, service_id)
        if (
            stored_business is None
            or service is None
            or service.business_id != stored_business.id
            or not service.is_active
        ):
            raise PublicBookingUnavailable("This booking page is unavailable.")
        # The owner preview entrypoint requires an owner; the algorithm is reused below
        # with the same persisted scheduling inputs and no customer data.
        from takdora.availability import calculate_slots
        from takdora.models import BookingRules, DateClosure, WeeklyAvailabilityBlock

        blocks = list(
            session.exec(
                select(WeeklyAvailabilityBlock).where(
                    WeeklyAvailabilityBlock.business_id == stored_business.id
                )
            ).all()
        )
        rules = session.exec(
            select(BookingRules).where(BookingRules.business_id == stored_business.id)
        ).first()
        closures = set(
            session.exec(
                select(DateClosure.local_date).where(DateClosure.business_id == stored_business.id)
            ).all()
        )
    if rules is None:
        rules = BookingRules(business_id=stored_business.id or 0)
    # Cover the visitor-local date's UTC edges by asking for adjacent business weeks.
    first_local = datetime.combine(
        visitor_day, datetime.min.time(), tzinfo=visitor_zone
    ).astimezone(UTC)
    last_local = first_local + timedelta(days=1)
    weeks = {
        (first_local.astimezone(ZoneInfo(business.timezone)).date() - timedelta(days=offset))
        for offset in range(7)
    }
    candidate_slots: dict[datetime, AvailabilitySlot] = {}
    for candidate_day in weeks:
        week_start = candidate_day - timedelta(days=candidate_day.weekday())
        from takdora.availability import calculate_slots

        for slot in calculate_slots(
            service=service,
            timezone_name=business.timezone,
            blocks=blocks,
            rules=rules,
            week_start=week_start,
            closures=closures,
            now=now,
        ):
            if first_local <= slot.start_at_utc < last_local:
                candidate_slots[slot.start_at_utc] = slot
    return tuple(candidate_slots[key] for key in sorted(candidate_slots))
