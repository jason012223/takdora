"""Owner-only booking projections and lifecycle commands."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from zoneinfo import ZoneInfo

import reflex as rx
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from takdora.availability import OccupiedInterval, calculate_slots
from takdora.booking import ACTIVE_BOOKING_STATUSES
from takdora.models import (
    Booking,
    BookingChangeOutbox,
    BookingOperationAudit,
    BookingRules,
    Business,
    BusinessService,
    DateClosure,
    OwnerAccount,
    WeeklyAvailabilityBlock,
)
from takdora.tenancy import WorkspaceAccessError, get_workspace_for_owner, require_owner

BOOKING_STATUSES = ("pending", "scheduled", "cancelled", "completed")
BOOKING_STATUS_LABELS = {
    "pending": "Pending",
    "scheduled": "Scheduled",
    "cancelled": "Cancelled",
    "completed": "Completed",
}
MAX_CUSTOMER_MESSAGE_LENGTH = 500


@dataclass(frozen=True)
class BookingProjection:
    id: int
    status: str
    status_label: str
    service_name: str
    starts_at: datetime
    ends_at: datetime
    local_time: str
    customer_name: str = ""
    customer_email: str = ""
    customer_phone: str = ""
    customer_note: str = ""


@dataclass(frozen=True)
class BookingOperationResult:
    outcome: str
    message: str
    booking: BookingProjection | None = None


def _business_for_owner(owner: OwnerAccount | None) -> Business:
    return get_workspace_for_owner(require_owner(owner)) or (_ for _ in ()).throw(
        WorkspaceAccessError("Booking not found.")
    )


def normalize_status(value: str) -> str:
    return value if value in BOOKING_STATUSES else ""


def normalize_date(value: str, *, fallback: date | None = None) -> date:
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError):
        return fallback or datetime.now(UTC).date()


def _projection(
    booking: Booking, service: BusinessService, *, details: bool = False
) -> BookingProjection:
    local = booking.starts_at.astimezone(ZoneInfo(booking.business_timezone))
    return BookingProjection(
        id=booking.id or 0,
        status=booking.status,
        status_label=BOOKING_STATUS_LABELS.get(booking.status, "Scheduled"),
        service_name=service.name,
        starts_at=booking.starts_at,
        ends_at=booking.ends_at,
        local_time=(
            f"{local.strftime('%a, %b')} {local.day}, "
            f"{local.strftime('%I:%M %p').lstrip('0')} ({booking.business_timezone})"
        ),
        customer_name=booking.customer_name if details else "",
        customer_email=booking.customer_email if details else "",
        customer_phone=booking.customer_phone or "" if details else "",
        customer_note=booking.customer_note or "" if details else "",
    )


def owner_bookings(
    owner: OwnerAccount | None, *, selected_date: str = "", status: str = ""
) -> tuple[BookingProjection, ...]:
    """Return one bounded local-day agenda, always scoped before record projection."""
    business = _business_for_owner(owner)
    day = normalize_date(selected_date)
    zone = ZoneInfo(business.timezone)
    start = datetime.combine(day, datetime.min.time(), tzinfo=zone).astimezone(UTC)
    end = start + timedelta(days=1)
    with rx.session() as session:
        statement = select(Booking).where(
            Booking.business_id == business.id, Booking.starts_at >= start, Booking.starts_at < end
        )
        if normalized := normalize_status(status):
            statement = statement.where(Booking.status == normalized)
        bookings = list(session.exec(statement.order_by(Booking.starts_at)).all())
        services = {
            item.id: item
            for item in session.exec(
                select(BusinessService).where(BusinessService.business_id == business.id)
            ).all()
        }
    return tuple(
        _projection(item, services[item.service_id])
        for item in bookings
        if item.service_id in services
    )


def owner_week_bookings(
    owner: OwnerAccount | None, *, selected_date: str = "", status: str = ""
) -> tuple[BookingProjection, ...]:
    business = _business_for_owner(owner)
    day = normalize_date(selected_date)
    week_start = day - timedelta(days=day.weekday())
    zone = ZoneInfo(business.timezone)
    start = datetime.combine(week_start, datetime.min.time(), tzinfo=zone).astimezone(UTC)
    end = start + timedelta(days=7)
    with rx.session() as session:
        statement = select(Booking).where(
            Booking.business_id == business.id, Booking.starts_at >= start, Booking.starts_at < end
        )
        if normalized := normalize_status(status):
            statement = statement.where(Booking.status == normalized)
        bookings = list(session.exec(statement.order_by(Booking.starts_at)).all())
        services = {
            item.id: item
            for item in session.exec(
                select(BusinessService).where(BusinessService.business_id == business.id)
            ).all()
        }
    return tuple(
        _projection(item, services[item.service_id])
        for item in bookings
        if item.service_id in services
    )


def owner_booking_detail(
    owner: OwnerAccount | None, booking_id: int | str
) -> BookingProjection | None:
    try:
        record_id = int(booking_id)
    except (TypeError, ValueError):
        return None
    try:
        business = _business_for_owner(owner)
    except WorkspaceAccessError:
        return None
    with rx.session() as session:
        booking = session.exec(
            select(Booking).where(Booking.business_id == business.id, Booking.id == record_id)
        ).first()
        if booking is None:
            return None
        service = session.get(BusinessService, booking.service_id)
        return _projection(booking, service, details=True) if service else None


def _audit(
    session: rx.Model,
    booking: Booking,
    owner: OwnerAccount,
    action: str,
    prior: str,
    metadata: str = "",
) -> None:
    session.add(
        BookingOperationAudit(
            business_id=booking.business_id,
            booking_id=booking.id or 0,
            actor_owner_id=owner.id or 0,
            action=action,
            prior_status=prior,
            new_status=booking.status,
            audit_details=metadata,
        )
    )


def _operation_projection(session: rx.Model, booking: Booking) -> BookingProjection | None:
    service = session.get(BusinessService, booking.service_id)
    return _projection(booking, service, details=True) if service else None


def cancel_booking(
    owner: OwnerAccount | None, booking_id: int | str, customer_message: str = ""
) -> BookingOperationResult:
    """Cancel only an owned eligible appointment and queue a post-commit update."""
    message = customer_message.strip()
    if len(message) > MAX_CUSTOMER_MESSAGE_LENGTH:
        return BookingOperationResult(
            "validation_error", "Keep the customer message under 500 characters."
        )
    try:
        business = _business_for_owner(owner)
        authorized_owner = require_owner(owner)
        record_id = int(booking_id)
    except (WorkspaceAccessError, ValueError, TypeError):
        return BookingOperationResult("not_found", "Booking not found.")
    with rx.session() as session:
        booking = session.exec(
            select(Booking)
            .where(Booking.business_id == business.id, Booking.id == record_id)
            .with_for_update()
        ).first()
        if booking is None:
            return BookingOperationResult("not_found", "Booking not found.")
        if booking.status not in ("pending", "scheduled"):
            return BookingOperationResult(
                "invalid_state",
                "This booking cannot be cancelled.",
                _operation_projection(session, booking),
            )
        prior = booking.status
        booking.status = "cancelled"
        _audit(session, booking, authorized_owner, "cancelled", prior, message)
        session.add(booking)
        session.add(
            BookingChangeOutbox(
                business_id=booking.business_id,
                booking_id=booking.id or 0,
                message_type="cancelled",
                recipient_email=booking.customer_email,
                customer_message=message or None,
            )
        )
        session.commit()
        return BookingOperationResult(
            "cancelled", "Booking cancelled.", _operation_projection(session, booking)
        )


def complete_booking(owner: OwnerAccount | None, booking_id: int | str) -> BookingOperationResult:
    try:
        business = _business_for_owner(owner)
        authorized_owner = require_owner(owner)
        record_id = int(booking_id)
    except (WorkspaceAccessError, ValueError, TypeError):
        return BookingOperationResult("not_found", "Booking not found.")
    with rx.session() as session:
        booking = session.exec(
            select(Booking)
            .where(Booking.business_id == business.id, Booking.id == record_id)
            .with_for_update()
        ).first()
        if booking is None:
            return BookingOperationResult("not_found", "Booking not found.")
        if booking.status != "scheduled":
            return BookingOperationResult(
                "invalid_state",
                "Only scheduled bookings can be completed.",
                _operation_projection(session, booking),
            )
        booking.status = "completed"
        _audit(session, booking, authorized_owner, "completed", "scheduled")
        session.add(booking)
        session.commit()
        return BookingOperationResult(
            "completed", "Booking marked completed.", _operation_projection(session, booking)
        )


def replacement_slots(owner: OwnerAccount | None, booking_id: int | str, week_start: date) -> tuple:
    """Return server-computed available slots, excluding just the booking being moved."""
    detail = owner_booking_detail(owner, booking_id)
    if detail is None or detail.status != "scheduled":
        return ()
    business = _business_for_owner(owner)
    with rx.session() as session:
        booking = session.get(Booking, detail.id)
        service = session.get(BusinessService, booking.service_id) if booking else None
        if service is None or not service.is_active:
            return ()
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
                    Booking.id != booking.id,
                )
            ).all()
        )
    return calculate_slots(
        service=service,
        timezone_name=business.timezone,
        blocks=blocks,
        rules=rules,
        week_start=week_start,
        closures=closures,
        occupied=occupied,
    )


def reschedule_booking(
    owner: OwnerAccount | None, booking_id: int | str, slot_start_utc: str
) -> BookingOperationResult:
    try:
        business = _business_for_owner(owner)
        authorized_owner = require_owner(owner)
        record_id = int(booking_id)
        selected = datetime.fromisoformat(slot_start_utc.replace("Z", "+00:00")).astimezone(UTC)
    except (WorkspaceAccessError, ValueError, TypeError):
        return BookingOperationResult("validation_error", "Choose an available replacement time.")
    with rx.session() as session:
        booking = session.exec(
            select(Booking)
            .where(Booking.business_id == business.id, Booking.id == record_id)
            .with_for_update()
        ).first()
        if booking is None:
            return BookingOperationResult("not_found", "Booking not found.")
        if booking.status != "scheduled":
            return BookingOperationResult(
                "invalid_state",
                "This booking cannot be rescheduled.",
                _operation_projection(session, booking),
            )
    choices = replacement_slots(
        owner,
        record_id,
        selected.astimezone(ZoneInfo(business.timezone)).date()
        - timedelta(days=selected.weekday()),
    )
    choice = next((item for item in choices if item.start_at_utc == selected), None)
    if choice is None:
        return BookingOperationResult("slot_taken", "That replacement time is no longer available.")
    with rx.session() as session:
        booking = session.exec(
            select(Booking)
            .where(Booking.business_id == business.id, Booking.id == record_id)
            .with_for_update()
        ).first()
        if booking is None or booking.status != "scheduled":
            return BookingOperationResult(
                "slot_taken", "That replacement time is no longer available."
            )
        old_time = booking.starts_at.isoformat()
        booking.starts_at, booking.ends_at, booking.business_timezone = (
            choice.start_at_utc,
            choice.end_at_utc,
            business.timezone,
        )
        _audit(
            session,
            booking,
            authorized_owner,
            "rescheduled",
            "scheduled",
            f"from={old_time};to={choice.start_at_utc.isoformat()}",
        )
        session.add(booking)
        try:
            session.add(
                BookingChangeOutbox(
                    business_id=booking.business_id,
                    booking_id=booking.id or 0,
                    message_type="rescheduled",
                    recipient_email=booking.customer_email,
                )
            )
            session.commit()
        except IntegrityError:
            session.rollback()
            return BookingOperationResult(
                "slot_taken", "That replacement time is no longer available."
            )
        return BookingOperationResult(
            "rescheduled", "Booking rescheduled.", _operation_projection(session, booking)
        )
