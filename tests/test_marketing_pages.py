"""Marketing routes keep a factual path into the real registration flow."""

from takdora.pages.marketing import home_page


def test_home_page_builds_with_primary_registration_and_secondary_demo_links() -> None:
    rendered = str(home_page())
    assert "Create your business" in rendered
    assert '"/register"' in rendered
    assert "Explore the demo" in rendered
    assert '"/demo"' in rendered
    assert "Booking and invoicing" in rendered
