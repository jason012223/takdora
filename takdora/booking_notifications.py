"""Post-commit booking confirmation rendering and durable delivery updates."""

from __future__ import annotations

from datetime import UTC, datetime
from zoneinfo import ZoneInfo

import reflex as rx
from sqlmodel import select

from takdora.config import get_settings
from takdora.mailer import MailDeliveryError, Mailer
from takdora.models import Booking, BookingConfirmationOutbox, Business, BusinessService


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
