"""Real-browser public booking smoke check, enabled only with reachable Compose ports."""

from __future__ import annotations

import os

import pytest


@pytest.mark.skipif(
    os.getenv("TAKDORA_RUN_E2E") != "1",
    reason="Requires reachable Compose frontend/backend ports and an active published fixture.",
)
def test_published_business_page_loads_in_a_real_browser(app_base_url: str) -> None:
    from playwright.sync_api import sync_playwright

    slug = os.environ["TAKDORA_E2E_PUBLISHED_SLUG"]
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page()
        page.goto(f"{app_base_url}/b/{slug}", wait_until="networkidle")
        assert page.locator("#public-booking-form").is_visible()
        browser.close()
