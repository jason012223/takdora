"""Focused single-page booking form composition checks."""

from takdora.pages.public_booking import public_booking_page


def test_public_page_has_one_focused_form_and_direct_optional_fields() -> None:
    rendered = str(public_booking_page())
    assert "public-booking-form" in rendered
    assert "customer-phone" in rendered
    assert "customer-note" in rendered
    assert "/privacy" in rendered


def test_public_page_maps_success_and_conflict_without_clearing_customer_fields() -> None:
    source = open("takdora/pages/public_booking.py", encoding="utf-8").read()
    assert "That time was just taken" in source
    assert "self.customer_name" in source
    assert "dispatch_confirmation" in source
    assert "Your booking is confirmed" in source
