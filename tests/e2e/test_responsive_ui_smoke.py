"""Desktop and mobile browser smoke coverage for the UI preview route."""

from playwright.sync_api import expect, sync_playwright


def test_responsive_preview_renders_without_horizontal_overflow(app_base_url: str) -> None:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            for viewport in ({"width": 1280, "height": 900}, {"width": 390, "height": 844}):
                page = browser.new_page(viewport=viewport)
                page.goto(
                    f"{app_base_url}/ui-preview", wait_until="domcontentloaded", timeout=60_000
                )
                expect(
                    page.get_by_role("heading", name="Sample service-business workflow")
                ).to_be_visible()
                expect(page.get_by_label("Sample customer name")).to_be_visible()
                assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
                page.close()
        finally:
            browser.close()
