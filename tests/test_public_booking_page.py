"""Focused single-page booking form composition checks."""

from takdora.pages.public_booking import public_booking_page


def test_public_page_has_one_focused_form_and_direct_optional_fields() -> None:
    rendered = str(public_booking_page())
    assert "public-booking-form" in rendered
    assert "customer-phone" in rendered
    assert "customer-note" in rendered
    assert "/privacy" in rendered
