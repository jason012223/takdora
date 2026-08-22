"""Security-focused owner authentication tests."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from takdora.auth import (
    SessionCredentialError,
    create_password_digest,
    create_session_credential,
    digest_token,
    normalize_email,
    verify_password,
    verify_session_credential,
)


def test_passwords_are_normalized_and_one_way_derived() -> None:
    normalized = normalize_email("  OWNER@Example.COM ")
    digest, salt = create_password_digest("correct horse battery staple")

    assert normalized == "owner@example.com"
    assert digest != "correct horse battery staple"
    assert salt
    assert verify_password("correct horse battery staple", digest, salt)
    assert not verify_password("incorrect", digest, salt)


def test_session_credentials_are_opaque_and_expire_or_revoke_server_side() -> None:
    raw, digest = create_session_credential()
    assert raw != digest
    assert verify_session_credential(raw, digest, datetime.now(UTC) + timedelta(hours=1))
    assert not verify_session_credential(raw, digest, datetime.now(UTC) - timedelta(seconds=1))
    assert not verify_session_credential(
        raw, digest, datetime.now(UTC) + timedelta(hours=1), revoked=True
    )


def test_session_expiry_accepts_utc_naive_database_timestamps() -> None:
    raw, digest = create_session_credential()

    assert verify_session_credential(
        raw, digest, (datetime.now(UTC) + timedelta(hours=1)).replace(tzinfo=None)
    )


@pytest.mark.parametrize("credential", ["", "malformed", "x" * 10])
def test_malformed_session_credentials_are_denied(credential: str) -> None:
    with pytest.raises(SessionCredentialError):
        digest_token(credential, minimum_length=20)
