"""Tests for one-time, non-enumerating password reset credentials."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from takdora.auth import (
    AuthenticationError,
    build_public_token_url,
    create_one_time_token,
    reset_token_is_usable,
)
from takdora.config import ConfigurationError, get_settings
from takdora.mailer import InMemoryMailer, MailDeliveryError


def test_reset_tokens_are_one_time_and_expire_in_thirty_minutes() -> None:
    raw, digest = create_one_time_token()
    expiry = datetime.now(UTC) + timedelta(minutes=30)

    assert raw != digest
    assert reset_token_is_usable(raw, digest, expiry, consumed_at=None)
    assert not reset_token_is_usable(raw, digest, expiry, consumed_at=datetime.now(UTC))
    assert not reset_token_is_usable(
        raw, digest, datetime.now(UTC) - timedelta(seconds=1), consumed_at=None
    )


def test_reset_token_expiry_accepts_utc_naive_database_timestamps() -> None:
    raw, digest = create_one_time_token()

    assert reset_token_is_usable(
        raw,
        digest,
        (datetime.now(UTC) + timedelta(hours=1)).replace(tzinfo=None),
        consumed_at=None,
    )


def test_reset_urls_are_absolute_and_do_not_leak_email() -> None:
    url = build_public_token_url("https://takdora.app", "/reset-password", "safe-token-value")
    assert url == "https://takdora.app/reset-password?token=safe-token-value"
    assert "@" not in url


@pytest.mark.parametrize(
    "origin", ["http://takdora.app", "takdora.app", "https://takdora.app/path"]
)
def test_production_settings_reject_unsafe_mail_setup(origin: str) -> None:
    with pytest.raises(ConfigurationError):
        get_settings(
            {
                "APP_ENV": "production",
                "DATABASE_URL": "postgresql+psycopg://example",
                "API_URL": "https://takdora.app/api",
                "APP_SECRET_KEY": "test-secret",
                "PUBLIC_APP_ORIGIN": origin,
            }
        )


def test_new_password_policy_is_shared_with_registration() -> None:
    with pytest.raises(AuthenticationError):
        # The implementation must use the registration password policy too.
        from takdora.auth import validate_password

        validate_password("short")


def test_mailer_sends_only_absolute_one_time_links_with_safe_failure() -> None:
    mailer = InMemoryMailer()
    mailer.send_password_reset("owner@example.com", "https://takdora.app/reset-password?token=safe")
    assert len(mailer.sent_messages) == 1
    assert "https://takdora.app/reset-password?token=safe" in mailer.sent_messages[0].body
    assert "correct horse battery staple" not in mailer.sent_messages[0].body

    failing_mailer = InMemoryMailer(fail_delivery=True)
    with pytest.raises(MailDeliveryError, match="try again"):
        failing_mailer.send_verification(
            "owner@example.com", "https://takdora.app/verify-email?token=safe"
        )
