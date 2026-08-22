"""Authoritative anonymous booking command; browser slots remain advisory."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import reflex as rx
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from takdora.auth import AuthenticationError, normalize_email
from takdora.availability import OccupiedInterval, calculate_slots
from takdora.models import (
    Booking,
    BookingConfirmationOutbox,
    BookingRules,
    Business,
    BusinessService,
    DateClosure,
    WeeklyAvailabilityBlock,
)
from takdora.public_booking import _is_publicly_available

ACTIVE_BOOKING_STATUSES = ("pending", "scheduled", "completed")
MAX_NAME_LENGTH = 120
MAX_PHONE_LENGTH = 48
MAX_NOTE_LENGTH = 1000
_IDEMPOTENCY_PATTERN = re.compile(r"^[A-Za-z0-9_-]{24,96}$")


@dataclass(frozen=True)
class BookingRequest:
    slug: str
    service_id: int | str
    slot_start_utc: str
    idempotency_key: str
    customer_name: str
    customer_email: str
    customer_phone: str = ""
    customer_note: str = ""
    browser_timezone: str = ""
    honeypot: str = ""


@dataclass(frozen=True)
class BookingResult:
    outcome: str
    booking_id: int | None = None
    message: str = ""


def _parse_request(request: BookingRequest) -> tuple[int, datetime, str, str, str, str, str]:
    if request.honeypot.strip():
        raise ValueError("We could not accept that booking. Please try again.")
    if not _IDEMPOTENCY_PATTERN.fullmatch(request.idempotency_key):
        raise ValueError("Please refresh and try booking again.")
    name = request.customer_name.strip()
    if not name or len(name) > MAX_NAME_LENGTH:
        raise ValueError("Enter your name using 120 characters or fewer.")
    try:
        email = normalize_email(request.customer_email)
    except AuthenticationError as error:
        raise ValueError("Enter a valid email address.") from error
    phone = request.customer_phone.strip()
    note = request.customer_note.strip()
    if len(phone) > MAX_PHONE_LENGTH or len(note) > MAX_NOTE_LENGTH:
        raise ValueError("Please shorten your phone number or note.")
    try:
        service_id = int(request.service_id)
        instant = datetime.fromisoformat(request.slot_start_utc.replace("Z", "+00:00"))
    except (TypeError, ValueError) as error:
        raise ValueError("Choose an available appointment time.") from error
    if instant.tzinfo is None:
        raise ValueError("Choose an available appointment time.")
    if request.browser_timezone:
        try:
            ZoneInfo(request.browser_timezone)
        except ZoneInfoNotFoundError as error:
            raise ValueError("Your time zone is unavailable. Refresh and try again.") from error
    return service_id, instant.astimezone(UTC), name, email, phone, note, request.idempotency_key


def create_public_booking(request: BookingRequest) -> BookingResult:
    """Create one scheduled appointment after a transaction-local slot recheck."""
    try:
        service_id, instant, name, email, phone, note, key = _parse_request(request)
    except ValueError as error:
        return BookingResult("validation_error", message=str(error))
    try:
        with rx.session() as session:
            business = session.exec(
                select(Business).where(Business.slug == request.slug).with_for_update()
            ).first()
            if business is None or not _is_publicly_available(business):
                return BookingResult(
                    "validation_error", message="This booking page is unavailable."
                )
            existing = session.exec(
                select(Booking).where(
                    Booking.business_id == business.id, Booking.idempotency_key == key
                )
            ).first()
            if existing is not None:
                return BookingResult(
                    "booked", booking_id=existing.id, message="Booking already saved."
                )
            service = session.get(BusinessService, service_id)
            if service is None or service.business_id != business.id or not service.is_active:
                return BookingResult("validation_error", message="Choose an available service.")
            blocks = list(
                session.exec(
                    select(WeeklyAvailabilityBlock).where(
                        WeeklyAvailabilityBlock.business_id == business.id
                    )
                ).all()
            )
            rules = session.exec(
                select(BookingRules).where(BookingRules.business_id == business.id)
            ).first() or BookingRules(business_id=business.id or 0)
            closures = set(
                session.exec(
                    select(DateClosure.local_date).where(DateClosure.business_id == business.id)
                ).all()
            )
            occupied = tuple(
                OccupiedInterval(item.starts_at, item.ends_at, item.status)
                for item in session.exec(
                    select(Booking).where(
                        Booking.business_id == business.id,
                        Booking.status.in_(ACTIVE_BOOKING_STATUSES),
                    )
                ).all()
            )
            local_day = instant.astimezone(ZoneInfo(business.timezone)).date()
            available = calculate_slots(
                service=service,
                timezone_name=business.timezone,
                blocks=blocks,
                rules=rules,
                week_start=local_day - timedelta(days=local_day.weekday()),
                closures=closures,
                occupied=occupied,
            )
            slot = next((item for item in available if item.start_at_utc == instant), None)
            if slot is None:
                return BookingResult(
                    "slot_taken", message="That time was just taken. Choose another time."
                )
            booking = Booking(
                business_id=business.id or 0,
                service_id=service.id or 0,
                customer_name=name,
                customer_email=email,
                customer_phone=phone or None,
                customer_note=note or None,
                starts_at=slot.start_at_utc,
                ends_at=slot.end_at_utc,
                business_timezone=business.timezone,
                idempotency_key=key,
            )
            session.add(booking)
            session.flush()
            session.add(
                BookingConfirmationOutbox(
                    business_id=business.id or 0,
                    booking_id=booking.id or 0,
                    recipient_email=booking.customer_email,
                )
            )
            session.commit()
            session.refresh(booking)
            return BookingResult("booked", booking_id=booking.id, message="Booking confirmed.")
    except IntegrityError:
        return BookingResult("slot_taken", message="That time was just taken. Choose another time.")
