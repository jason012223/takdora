"""Browser smoke coverage for the real local Reflex application."""

from __future__ import annotations

from playwright.sync_api import expect, sync_playwright


def test_readiness_control_and_healthz_work_against_compose(app_base_url: str) -> None:
    """A browser can use the live probe without seeing configuration details."""
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page()
        # A fresh Reflex frontend compile can take longer than a warm dev server.
        page.set_default_timeout(30_000)
        try:
            page.goto(app_base_url, wait_until="domcontentloaded", timeout=60_000)
            control = page.locator("#readiness-control")
            expect(control).to_be_visible()
            control.click()
            expect(page.locator("#readiness-result")).to_contain_text(
                "Database readiness confirmed"
            )
            health = page.request.get("http://localhost:8000/healthz")
            assert health.status == 200
            assert health.json() == {"status": "ok"}
        finally:
            browser.close()
