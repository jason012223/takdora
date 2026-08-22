"""Business setup validation and publication-readiness tests."""

from __future__ import annotations

import pytest

from takdora.business_setup import (
    BusinessProfileInput,
    default_branding,
    evaluate_publish_readiness,
    normalize_slug,
    slug_change_plan,
    validate_profile,
)


def test_philippines_first_profile_defaults_and_optional_branding() -> None:
    branding = default_branding(None, None)
    assert branding.logo_label == "Takdora"
    assert branding.accent_color
    profile = BusinessProfileInput(name="Luna Studio")
    validated = validate_profile(profile)
    assert validated.timezone == "Asia/Manila"
    assert validated.currency == "PHP"


@pytest.mark.parametrize("value", ["Luna Studio", "luna--studio", " LUNA studio "])
def test_slug_is_editable_but_normalized_for_public_urls(value: str) -> None:
    assert normalize_slug(value) == "luna-studio"


@pytest.mark.parametrize("value", ["bad slug!", "", "https://example.com"])
def test_invalid_public_slug_is_rejected(value: str) -> None:
    with pytest.raises(ValueError):
        normalize_slug(value)


def test_publish_readiness_names_each_missing_prerequisite() -> None:
    readiness = evaluate_publish_readiness(
        email_verified=False,
        business_name="Luna Studio",
        slug="luna-studio",
        has_active_service=False,
        has_working_hours=False,
    )
    assert readiness.ready is False
    assert readiness.missing_required == ("Verify email", "Add a service", "Set working hours")


def test_published_slug_changes_keep_a_permanent_redirect_record() -> None:
    change = slug_change_plan("luna-studio", "luna-wellness", is_published=True)
    assert change.canonical_slug == "luna-wellness"
    assert change.redirect_from == "luna-studio"
