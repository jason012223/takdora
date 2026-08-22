"""Synthetic demo authority is derived server-side and disabled by default."""

from dataclasses import replace

import pytest

from takdora.config import get_settings
from takdora.demo import DEMO_EMAIL, DemoUnavailable, enter_synthetic_demo, reset_synthetic_demo


def test_synthetic_demo_is_disabled_without_a_server_only_feature_switch() -> None:
    settings = replace(get_settings(), synthetic_demo_enabled=False)
    with pytest.raises(DemoUnavailable):
        reset_synthetic_demo(settings)
    with pytest.raises(DemoUnavailable):
        enter_synthetic_demo(settings)


def test_demo_identity_uses_a_reserved_example_domain() -> None:
    assert DEMO_EMAIL.endswith(".example")


def test_reset_uses_only_synthetic_records_and_no_mailer() -> None:
    source = open("takdora/demo.py", encoding="utf-8").read()
    assert "is_synthetic_demo" in source
    assert "Mailer(" not in source
    assert "@takdora.example" in source
