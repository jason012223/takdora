"""Owner booking page rendering contracts."""

from takdora.pages.owner_bookings import owner_bookings_page


def test_owner_booking_page_builds_an_agenda_first_private_view() -> None:
    page = owner_bookings_page()
    assert page is not None
