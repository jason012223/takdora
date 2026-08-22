"""Public, labelled entry surface for the isolated portfolio fixture."""

from __future__ import annotations

import reflex as rx

from takdora.auth import AuthState
from takdora.config import get_settings
from takdora.demo import DEMO_LABEL, DEMO_SLUG, DemoUnavailable, enter_synthetic_demo
from takdora.ui.layouts import marketing_layout


class DemoState(AuthState):
    message: str = ""

    def enter(self) -> rx.event.EventSpec | None:
        try:
            self.session_credential = enter_synthetic_demo(get_settings())
        except DemoUnavailable:
            self.message = "The synthetic demo is unavailable. Create your business to get started."
            return None
        return rx.redirect("/owner")


def demo_page() -> rx.Component:
    return marketing_layout(
        rx.vstack(
            rx.badge(DEMO_LABEL, color_scheme="orange", variant="soft"),
            rx.heading("Inspect a synthetic Takdora workspace", size="8"),
            rx.text(
                "Review a synthetic public booking page, completed booking, issued invoice, and "
                "manually tracked payment example. No visitor email is sent."
            ),
            rx.link("Open the synthetic public business", href=f"/b/{DEMO_SLUG}"),
            rx.button("Enter synthetic demo", on_click=DemoState.enter, color_scheme="orange"),
            rx.cond(DemoState.message != "", rx.text(DemoState.message, role="status")),
            rx.link("Create your business", href="/register"),
            spacing="4",
            align="start",
        )
    )
