"""Public booking boundary contracts that do not need a running database."""

from datetime import UTC, datetime

from takdora.availability import AvailabilitySlot
from takdora.public_booking import format_slot_for_timezone, valid_browser_timezone


def test_browser_timezone_is_only_a_validated_display_preference() -> None:
    assert valid_browser_timezone("America/Los_Angeles", fallback="Asia/Manila") == (
        "America/Los_Angeles",
        True,
    )
    assert valid_browser_timezone("not-a-zone", fallback="Asia/Manila") == ("Asia/Manila", False)


def test_utc_slot_formats_in_the_visitor_timezone_without_changing_identity() -> None:
    slot = AvailabilitySlot(
        start_at_utc=datetime(2026, 8, 24, 1, 0, tzinfo=UTC),
        end_at_utc=datetime(2026, 8, 24, 2, 0, tzinfo=UTC),
        local_label="private",
    )
    label, zone = format_slot_for_timezone(slot, "America/Los_Angeles")
    assert zone == "America/Los_Angeles"
    assert "Aug" in label
    assert slot.start_at_utc == datetime(2026, 8, 24, 1, 0, tzinfo=UTC)
