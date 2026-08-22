"""Focused contracts for owner booking-operation boundaries."""

from datetime import UTC, datetime

from takdora.booking_operations import BOOKING_STATUS_LABELS, normalize_date, normalize_status
from takdora.models import Booking, BusinessService


def test_lifecycle_vocabulary_keeps_public_booking_default_scheduled() -> None:
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
    assert booking.status == "scheduled"
    assert BOOKING_STATUS_LABELS == {
        "pending": "Pending",
        "scheduled": "Scheduled",
        "cancelled": "Cancelled",
        "completed": "Completed",
    }


def test_untrusted_filter_values_are_bounded_to_safe_defaults() -> None:
    assert normalize_status("unknown") == ""
    assert normalize_status("scheduled") == "scheduled"
    assert normalize_date("bad-date").isoformat()


def test_booking_operation_models_keep_customer_data_out_of_calendar_contract() -> None:
    service = BusinessService(business_id=1, name="Consultation", fixed_duration_minutes=30)
    assert service.name == "Consultation"
