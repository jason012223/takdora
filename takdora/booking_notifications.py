"""Post-commit booking confirmation rendering and durable delivery updates."""

from __future__ import annotations

from datetime import UTC, datetime
from zoneinfo import ZoneInfo

import reflex as rx
from sqlmodel import select

from takdora.config import get_settings
from takdora.mailer import MailDeliveryError, Mailer
from takdora.models import (
    Booking,
    BookingChangeOutbox,
    BookingConfirmationOutbox,
    Business,
    BusinessService,
)


def render_confirmation(
    booking: Booking, business: Business, service: BusinessService
) -> tuple[str, str]:
    """Return concise customer-safe content from committed snapshots only."""
    local_time = booking.starts_at.astimezone(ZoneInfo(booking.business_timezone))
    contact = business.contact_email or business.contact_phone or "the business directly"
    subject = f"Booking confirmed with {business.name}"
    body = (
        f"Your booking with {business.name} is confirmed.\n\n"
        f"Service: {service.name}\n"
        f"When: {local_time.strftime('%A, %B %d, %Y at %I:%M %p')} "
        f"({booking.business_timezone})\n"
        f"Questions? Contact {contact}."
    )
    return subject, body


def dispatch_confirmation(booking_id: int, *, mailer: Mailer | None = None) -> str:
    """Send only once after commit; a failed send leaves the appointment untouched."""
    with rx.session() as session:
        outbox = session.exec(
            select(BookingConfirmationOutbox).where(
                BookingConfirmationOutbox.booking_id == booking_id
            )
        ).first()
        if outbox is None:
            return "missing"
        if outbox.delivery_status == "sent":
            return "sent"
        booking = session.get(Booking, booking_id)
        business = session.get(Business, outbox.business_id)
        service = session.get(BusinessService, booking.service_id) if booking else None
        if booking is None or business is None or service is None:
            outbox.delivery_status = "failed"
            outbox.last_error = "booking_data_unavailable"
            outbox.updated_at = datetime.now(UTC)
            session.add(outbox)
            session.commit()
            return "delayed"
        subject, body = render_confirmation(booking, business, service)
        outbox.attempts += 1
        session.add(outbox)
        session.commit()
    try:
        (mailer or Mailer(get_settings())).send_booking_confirmation(
            outbox.recipient_email, subject, body
        )
    except MailDeliveryError:
        with rx.session() as session:
            stored = session.get(BookingConfirmationOutbox, outbox.id)
            if stored is not None:
                stored.delivery_status = "delayed"
                stored.last_error = "mail_delivery_failed"
                stored.updated_at = datetime.now(UTC)
                session.add(stored)
                session.commit()
        return "delayed"
    with rx.session() as session:
        stored = session.get(BookingConfirmationOutbox, outbox.id)
        if stored is not None:
            stored.delivery_status = "sent"
            stored.sent_at = datetime.now(UTC)
            stored.last_error = None
            stored.updated_at = datetime.now(UTC)
            session.add(stored)
            session.commit()
    return "sent"


def render_change_update(
    booking: Booking, business: Business, service: BusinessService, change: BookingChangeOutbox
) -> tuple[str, str]:
    """Render a bounded cancellation or reschedule email from committed data."""
    local_time = booking.starts_at.astimezone(ZoneInfo(booking.business_timezone))
    contact = business.contact_email or business.contact_phone or "the business directly"
    if change.message_type == "cancelled":
        subject = f"Booking cancelled with {business.name}"
        body = f"Your {service.name} booking with {business.name} has been cancelled."
        if change.customer_message:
            body += f"\n\nMessage from the business: {change.customer_message}"
    else:
        subject = f"Booking rescheduled with {business.name}"
        body = (
            f"Your {service.name} booking with {business.name} has been rescheduled.\n\n"
            f"New time: {local_time.strftime('%A, %B %d, %Y at %I:%M %p')} "
            f"({booking.business_timezone})"
        )
    return subject, f"{body}\n\nQuestions? Contact {contact}."


def dispatch_change_update(change_id: int, *, mailer: Mailer | None = None) -> str:
    """Deliver a committed lifecycle update once without affecting the booking."""
    with rx.session() as session:
        change = session.get(BookingChangeOutbox, change_id)
        if change is None:
            return "missing"
        if change.delivery_status == "sent":
            return "sent"
        booking = session.get(Booking, change.booking_id)
        business = session.get(Business, change.business_id)
        service = session.get(BusinessService, booking.service_id) if booking else None
        if booking is None or business is None or service is None:
            change.delivery_status = "delayed"
            change.last_error = "booking_data_unavailable"
            change.updated_at = datetime.now(UTC)
            session.add(change)
            session.commit()
            return "delayed"
        subject, body = render_change_update(booking, business, service, change)
        change.attempts += 1
        session.add(change)
        session.commit()
    try:
        (mailer or Mailer(get_settings())).send_booking_confirmation(
            change.recipient_email, subject, body
        )
    except MailDeliveryError:
        with rx.session() as session:
            stored = session.get(BookingChangeOutbox, change_id)
            if stored is not None:
                stored.delivery_status = "delayed"
                stored.last_error = "mail_delivery_failed"
                stored.updated_at = datetime.now(UTC)
                session.add(stored)
                session.commit()
        return "delayed"
    with rx.session() as session:
        stored = session.get(BookingChangeOutbox, change_id)
        if stored is not None:
            stored.delivery_status = "sent"
            stored.sent_at = datetime.now(UTC)
            stored.last_error = None
            stored.updated_at = datetime.now(UTC)
            session.add(stored)
            session.commit()
    return "sent"
