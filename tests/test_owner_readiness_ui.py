"""Owner setup guidance stays route-based and honest about publication."""

import inspect

from takdora.pages import onboarding, owner_dashboard


def test_dashboard_exposes_a_small_actionable_readiness_path() -> None:
    source = inspect.getsource(owner_dashboard)
    assert "Business readiness" in source
    assert "Finish details" in source
    assert "Add service" in source
    assert "Set hours" in source
    assert "Publish and preview" in source
    assert "publish_business" in source


def test_onboarding_routes_owners_to_the_next_real_tasks() -> None:
    source = inspect.getsource(onboarding)
    assert "/owner/services" in source
    assert "/owner/availability" in source
    assert "/owner" in source
