"""The small, accessible shell shared by early Takdora pages."""

from __future__ import annotations

import reflex as rx

from takdora.ui.theme import TOKENS, container_style


def brand_mark() -> rx.Component:
    """Render the text-based brand mark until a real mark is commissioned."""
    return rx.link(
        rx.hstack(
            rx.box(width="0.75rem", height="0.75rem", border_radius="999px", bg=TOKENS["brand"]),
            rx.text("Takdora", weight="bold", size="5", color=TOKENS["foreground"]),
            spacing="2",
            align="center",
        ),
        href="/",
        aria_label="Takdora home",
    )


def application_shell(*children: rx.Component) -> rx.Component:
    """Wrap page content in landmarks, a skip link, and a responsive frame."""
    return rx.box(
        rx.link("Skip to content", href="#main-content", class_name="skip-link"),
        rx.el.header(
            rx.hstack(
                brand_mark(),
                rx.text(
                    "Booking and invoices, in one clear place.", color=TOKENS["muted"], size="2"
                ),
                justify="between",
                align="center",
                **container_style,
                padding_y=TOKENS["space_4"],
            ),
            border_bottom="1px solid #E6DED0",
        ),
        rx.el.main(
            rx.vstack(*children, spacing="6", align="stretch"),
            id="main-content",
            min_height="calc(100vh - 9rem)",
            padding_y={"base": TOKENS["space_8"], "md": "4rem"},
            **container_style,
        ),
        rx.el.footer(
            rx.text(
                "Takdora is built for clear, dependable service-business operations.", size="2"
            ),
            color=TOKENS["muted"],
            border_top="1px solid #E6DED0",
            padding_y=TOKENS["space_6"],
            **container_style,
        ),
        min_height="100vh",
        bg=TOKENS["surface"],
        color=TOKENS["foreground"],
    )
