"""Customer-safe confirmation content contracts."""

from datetime import UTC, datetime

from takdora.booking_notifications import render_change_update, render_confirmation
from takdora.models import Booking, BookingChangeOutbox, Business, BusinessService


def test_confirmation_renders_only_customer_safe_appointment_details() -> None:
    booking = Booking(
        business_id=1,
        service_id=2,
        customer_name="Luna",
        customer_email="luna@example.com",
        starts_at=datetime(2026, 8, 24, 1, tzinfo=UTC),
        ends_at=datetime(2026, 8, 24, 2, tzinfo=UTC),
        business_timezone="Asia/Manila",
        idempotency_key="a" * 24,
    )
    business = Business(creating_owner_id=1, name="Luna Studio", contact_email="hello@luna.example")
    service = BusinessService(business_id=1, name="Haircut", fixed_duration_minutes=60)
    subject, body = render_confirmation(booking, business, service)
    assert "Luna Studio" in subject
    assert "Haircut" in body
    assert "Asia/Manila" in body
    assert "owner" not in body.casefold()


def test_change_update_is_customer_safe_and_can_include_an_optional_message() -> None:
    booking = Booking(
        business_id=1,
        service_id=2,
        customer_name="Luna",
        customer_email="luna@example.com",
        starts_at=datetime(2026, 8, 24, 1, tzinfo=UTC),
        ends_at=datetime(2026, 8, 24, 2, tzinfo=UTC),
        business_timezone="Asia/Manila",
        idempotency_key="a" * 24,
    )
    change = BookingChangeOutbox(
        business_id=1,
        booking_id=1,
        recipient_email="luna@example.com",
        message_type="cancelled",
        customer_message="Sorry for the change.",
    )
    business = Business(creating_owner_id=1, name="Luna Studio", contact_email="hello@luna.example")
    service = BusinessService(business_id=1, name="Haircut", fixed_duration_minutes=60)
    subject, body = render_change_update(booking, business, service, change)
    assert "cancelled" in subject.casefold()
    assert "Sorry for the change." in body
    assert "audit" not in body.casefold()
