"""Synthetic-only browser narrative for the portfolio reviewer flow."""

from __future__ import annotations

import os
from pathlib import Path

from playwright.sync_api import expect, sync_playwright


def _assert_no_overflow(page: object) -> None:
    assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")  # type: ignore[attr-defined]


def _capture(page: object, name: str) -> None:
    """Capture only the labelled synthetic workflow when an operator enables evidence."""
    evidence_dir = os.getenv("TAKDORA_EVIDENCE_DIR")
    if evidence_dir:
        Path(evidence_dir).mkdir(parents=True, exist_ok=True)
        page.screenshot(path=str(Path(evidence_dir) / f"{name}.png"), full_page=True)  # type: ignore[attr-defined]


def test_synthetic_demo_narrative_is_responsive(app_base_url: str) -> None:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            for viewport in ({"width": 1280, "height": 900}, {"width": 390, "height": 844}):
                page = browser.new_page(viewport=viewport)
                page.goto(f"{app_base_url}/demo", wait_until="domcontentloaded", timeout=60_000)
                expect(page.get_by_text("Synthetic demo", exact=True)).to_be_visible()
                expect(page.get_by_role("button", name="Enter synthetic demo")).to_be_visible()
                _assert_no_overflow(page)
                page.get_by_role("button", name="Enter synthetic demo").click()
                expect(page).to_have_url(f"{app_base_url}/owner")
                expect(page.locator("#synthetic-demo-banner")).to_be_visible()
                _capture(page, f"owner-{viewport['width']}")
                page.goto(
                    f"{app_base_url}/b/takdora-demo-studio",
                    wait_until="domcontentloaded",
                    timeout=60_000,
                )
                expect(page.get_by_text("Synthetic consultation")).to_be_visible()
                _assert_no_overflow(page)
                page.goto(f"{app_base_url}/owner/invoices", wait_until="domcontentloaded")
                expect(page.locator("#synthetic-demo-banner")).to_be_visible()
                expect(page.get_by_text("Partially Paid", exact=True)).to_be_visible()
                _capture(page, f"invoice-{viewport['width']}")
                page.close()
        finally:
            browser.close()
