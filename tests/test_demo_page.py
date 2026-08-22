"""The public demo entry labels its data and preserves real registration."""

from takdora.pages.demo import demo_page


def test_demo_page_builds_with_synthetic_labels_and_real_registration_route() -> None:
    rendered = str(demo_page())
    assert "Synthetic demo" in rendered
    assert '"/register"' in rendered
    assert '"/b/takdora-demo-studio"' in rendered
