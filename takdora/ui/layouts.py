"""Responsive public, owner, and marketing layout factories."""

from __future__ import annotations

import reflex as rx

from takdora.ui.shell import brand_mark
from takdora.ui.theme import TOKENS, container_style


def _navigation(label: str, links: list[tuple[str, str]], *, owner: bool = False) -> rx.Component:
    return rx.el.nav(
        rx.hstack(
            brand_mark(),
            rx.hstack(
                *[rx.link(text, href=href, size="2") for text, href in links],
                display={"base": "none", "md": "flex"},
                spacing="3",
                flex_wrap="wrap",
                justify="end",
            ),
            rx.menu.root(
                rx.menu.trigger(rx.button("Menu", variant="soft", aria_label=f"{label} menu")),
                rx.menu.content(
                    *[rx.menu.item(rx.link(text, href=href, size="2")) for text, href in links]
                ),
                display={"base": "inline-flex", "md": "none"},
            ),
            justify="between",
            align="center",
            **container_style,
            padding_y="1rem",
        ),
        aria_label=label,
        border_bottom="1px solid #E6DED0",
        data_owner_navigation="true" if owner else "false",
    )


def public_layout(*children: rx.Component) -> rx.Component:
    return rx.box(
        rx.link("Skip to content", href="#preview-main", class_name="skip-link"),
        _navigation("Public navigation", [("Book", "#booking"), ("Contact", "#contact")]),
        rx.el.main(
            rx.vstack(*children, spacing="6"),
            id="preview-main",
            **container_style,
            padding_y="2rem",
        ),
        bg=TOKENS["surface"],
        min_height="100vh",
    )


def owner_layout(*children: rx.Component) -> rx.Component:
    return rx.box(
        _navigation(
            "Owner navigation", [("Bookings", "#bookings"), ("Invoices", "#invoices")], owner=True
        ),
        rx.el.main(
            rx.vstack(*children, spacing="6"),
            id="preview-main",
            **container_style,
            padding_y="2rem",
        ),
        bg=TOKENS["surface_subtle"],
        min_height="100vh",
    )


def marketing_layout(*children: rx.Component) -> rx.Component:
    return rx.box(
        rx.link("Skip to content", href="#preview-main", class_name="skip-link"),
        _navigation(
            "Marketing navigation",
            [
                ("How it works", "/#how-it-works"),
                ("Features", "/features"),
                ("Help", "/help"),
                ("Portfolio", "/portfolio"),
                ("Demo", "/demo"),
            ],
        ),
        rx.el.main(
            rx.vstack(*children, spacing="6"),
            id="preview-main",
            **container_style,
            padding_y="2rem",
        ),
        bg=TOKENS["surface"],
        min_height="100vh",
    )
