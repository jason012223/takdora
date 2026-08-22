"""Business setup validation and publication-readiness tests."""

from __future__ import annotations

import pytest

from takdora.business_setup import BusinessProfileInput, default_branding, normalize_slug, validate_profile


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
