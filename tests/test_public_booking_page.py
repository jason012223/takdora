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


def test_public_page_uses_hidden_select_values_and_an_explicit_review_summary() -> None:
    source = open("takdora/pages/public_booking.py", encoding="utf-8").read()
    assert '"label": f"{item.name}' in source
    assert '"id": str(item.id)' in source
    assert "Show available times" not in source
    assert "on_change=PublicBookingState.select_service" in source
    assert "Your appointment" in source
    assert "Review these details before booking." in source


def test_public_page_uses_outcome_appropriate_feedback_tones() -> None:
    source = open("takdora/pages/public_booking.py", encoding="utf-8").read()
    assert 'self.booking_message_kind = "success"' in source
    assert 'self.booking_message_kind = "warning"' in source
    assert 'self.booking_message_kind = "error"' in source
