"""Shared bounded waits for tests that target the running Compose stack."""

from __future__ import annotations

import os
import time
from http.client import HTTPException
from urllib.error import URLError
from urllib.request import urlopen

import pytest


@pytest.fixture(scope="session")
def app_base_url() -> str:
    """Wait briefly for the real Compose health endpoint before browser tests."""
    base_url = os.getenv("TAKDORA_TEST_BASE_URL", "http://localhost:3000")
    health_url = os.getenv("TAKDORA_TEST_HEALTH_URL", "http://localhost:8000/healthz")
    deadline = time.monotonic() + 45
    while time.monotonic() < deadline:
        try:
            with urlopen(health_url, timeout=2) as response:  # noqa: S310 - configured local test URL
                if response.status == 200:
                    return base_url
        except (HTTPException, OSError, URLError):
            pass
        time.sleep(1)
    pytest.fail(f"Takdora did not become ready at {health_url}")
