"""Playwright smoke test for the hydrated shared-component gallery."""

from playwright.sync_api import expect, sync_playwright


def test_design_system_gallery_loads(app_base_url: str) -> None:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page()
        try:
            page.goto(
                f"{app_base_url}/design-system", wait_until="domcontentloaded", timeout=60_000
            )
            expect(page.get_by_role("heading", name="Takdora interface patterns")).to_be_visible()
            expect(page.get_by_label("Customer name")).to_be_visible()
            expect(page.get_by_role("status")).to_be_visible()
        finally:
            browser.close()
