"""Compose-network browser checks for Takdora's real registration path."""

from playwright.sync_api import expect, sync_playwright


def test_marketing_registration_path_is_responsive_and_visible(app_base_url: str) -> None:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            for viewport in ({"width": 1280, "height": 900}, {"width": 390, "height": 844}):
                page = browser.new_page(viewport=viewport)
                page.goto(app_base_url, wait_until="domcontentloaded", timeout=60_000)
                expect(
                    page.get_by_role("heading", name="Booking and invoicing, in one clear place.")
                ).to_be_visible()
                registration = page.locator('a[href="/register"]').first
                expect(registration).to_be_visible()
                expect(page.locator('a[href="/demo"]').first).to_be_visible()
                assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
                registration.click()
                expect(page).to_have_url(f"{app_base_url}/register")
                page.close()
        finally:
            browser.close()
