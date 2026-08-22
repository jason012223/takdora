"""The preview primitive remains intentionally identity-free."""

from takdora.ui.primitives import availability_calendar


def test_availability_preview_source_does_not_accept_customer_fields() -> None:
    component = availability_calendar(
        [("Mon, Aug 24 · 9:00 AM", "Available"), ("10:00 AM", "Booked")]
    )
    rendered = str(component)
    assert "customer" in rendered.casefold()
    assert "email" not in rendered.casefold()
    assert "phone" not in rendered.casefold()
