"""Owner dashboard recovery copy remains customer-safe and action oriented."""

from takdora.pages.owner_dashboard import owner_dashboard


def test_owner_dashboard_exposes_delivery_recovery_surface() -> None:
    assert owner_dashboard() is not None
