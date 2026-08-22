"""Delivery retry policy contracts that do not require a live provider."""

from datetime import timedelta

from takdora.delivery import MAX_AUTOMATIC_ATTEMPTS, _backoff


def test_delivery_backoff_is_bounded_and_increases() -> None:
    assert _backoff(1) == timedelta(minutes=1)
    assert _backoff(2) == timedelta(minutes=2)
    assert _backoff(MAX_AUTOMATIC_ATTEMPTS) <= timedelta(minutes=60)


def test_delivery_attempt_cap_is_explicit() -> None:
    assert MAX_AUTOMATIC_ATTEMPTS == 5
