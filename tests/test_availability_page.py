"""Availability setup keeps the normal path clear and keyboard-operable."""

from takdora.pages.availability import WEEKDAYS, availability_page


def test_weekdays_are_owner_readable_and_keep_monday_first() -> None:
    assert WEEKDAYS == (
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    )


def test_availability_page_exposes_keyboard_move_and_optional_rules() -> None:
    rendered = str(availability_page())
    assert "Recurring working hours" in rendered
    assert "Move a working-hours block without dragging" in rendered
    assert "Keyboard and screen-reader friendly option" in rendered
    assert "Booking rules (optional)" in rendered
    assert "Close one date (optional)" in rendered
