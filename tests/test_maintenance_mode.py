"""Maintenance asset copy is bounded and gives visitors a useful next step."""

from pathlib import Path


def test_maintenance_page_is_branded_and_does_not_leak_technical_details() -> None:
    page = Path("docker/maintenance.html").read_text(encoding="utf-8")
    assert "temporarily unavailable" in page
    assert "contact the business directly" in page
    assert "DATABASE_URL" not in page
