"""The public demo entry labels its data and preserves real registration."""

from takdora.pages.demo import demo_page


def test_demo_page_builds_with_synthetic_labels_and_real_registration_route() -> None:
    rendered = str(demo_page())
    assert "Synthetic demo" in rendered
    assert '"/register"' in rendered
    assert '"/b/takdora-demo-studio"' in rendered


def test_owner_pages_contain_a_conditional_synthetic_demo_boundary() -> None:
    for path in (
        "takdora/pages/owner_dashboard.py",
        "takdora/pages/owner_bookings.py",
        "takdora/pages/owner_invoices.py",
    ):
        source = open(path, encoding="utf-8").read()
        assert "synthetic_demo_banner" in source
        assert "is_synthetic_demo" in source
