"""Booking command input contracts."""

from takdora.booking import BookingRequest, _parse_request, create_public_booking


def test_booking_request_rejects_malformed_customer_input_before_database_work() -> None:
    result = create_public_booking(
        BookingRequest("luna", "1", "not-a-date", "short", "", "not-email")
    )
    assert result.outcome == "validation_error"


def test_booking_request_normalizes_a_utc_instant_and_contact_snapshot() -> None:
    parsed = _parse_request(
        BookingRequest(
            "luna",
            "1",
            "2026-08-24T01:00:00Z",
            "a" * 24,
            " Luna ",
            "LUNA@example.com",
        )
    )
    assert parsed[1].isoformat() == "2026-08-24T01:00:00+00:00"
    assert parsed[2:4] == ("Luna", "luna@example.com")
