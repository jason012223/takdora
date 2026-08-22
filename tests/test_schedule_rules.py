"""Weekly-policy validation contracts."""

from datetime import time

import pytest

from takdora.availability import (
    BookingRulesInput,
    WeeklyBlockInput,
    _assert_non_overlapping,
    validate_booking_rules,
    validate_weekly_block,
)


def test_weekly_block_keeps_local_time_and_requires_an_ordered_day() -> None:
    block = validate_weekly_block(WeeklyBlockInput("0", "09:00", "12:00"))
    assert block.weekday == 0
    assert block.start_time == time(9)


@pytest.mark.parametrize(
    "block",
    [WeeklyBlockInput(7, "09:00", "10:00"), WeeklyBlockInput(0, "10:00", "10:00")],
)
def test_invalid_weekly_blocks_are_rejected(block: WeeklyBlockInput) -> None:
    with pytest.raises(ValueError):
        validate_weekly_block(block)


def test_touching_or_overlapping_blocks_are_rejected() -> None:
    with pytest.raises(ValueError, match="overlap or touch"):
        _assert_non_overlapping(
            [WeeklyBlockInput(0, "09:00", "12:00"), WeeklyBlockInput(0, "12:00", "14:00")]
        )


def test_defaults_and_bounded_optional_booking_rules() -> None:
    rules = validate_booking_rules(BookingRulesInput())
    assert rules.slot_interval_minutes == 30
    assert rules.minimum_lead_minutes == 60
    assert rules.booking_horizon_days == 30
    assert rules.buffer_minutes == 0
    with pytest.raises(ValueError):
        validate_booking_rules(BookingRulesInput(slot_interval_minutes=7))
