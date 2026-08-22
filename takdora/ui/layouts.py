"""Responsive public, owner, and marketing layout factories."""

from __future__ import annotations

import reflex as rx

from takdora.ui.shell import brand_mark
from takdora.ui.theme import TOKENS, container_style


class LayoutState(rx.State):
    """Small route-aware state shared by the private workspace navigation."""

    @rx.var
    def current_path(self) -> str:
        return self.router.page.path


def _owner_navigation_link(text: str, href: str) -> rx.Component:
    """Keep the active private destination obvious in both navigation variants."""
    return rx.cond(
        LayoutState.current_path == href,
        rx.link(
            text,
            href=href,
            size="2",
            weight="bold",
            color_scheme="orange",
            aria_current="page",
        ),
        rx.link(text, href=href, size="2"),
    )


def _navigation(label: str, links: list[tuple[str, str]], *, owner: bool = False) -> rx.Component:
    desktop_links = (
        [_owner_navigation_link(text, href) for text, href in links]
        if owner
        else [rx.link(text, href=href, size="2") for text, href in links]
    )
    mobile_links = (
        [rx.menu.item(_owner_navigation_link(text, href)) for text, href in links]
        if owner
        else [rx.menu.item(rx.link(text, href=href, size="2")) for text, href in links]
    )
    return rx.el.nav(
        rx.hstack(
            brand_mark(),
            rx.hstack(
                *desktop_links,
                display={"base": "none", "md": "flex"},
                spacing="3",
                flex_wrap="wrap",
                justify="end",
            ),
            rx.menu.root(
                rx.menu.trigger(rx.button("Menu", variant="soft", aria_label=f"{label} menu")),
                rx.menu.content(*mobile_links),
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
        _navigation("Public navigation", [("Home", "/"), ("Privacy", "/privacy")]),
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
        rx.link("Skip to workspace content", href="#preview-main", class_name="skip-link"),
        _navigation(
            "Owner navigation",
            [
                ("Dashboard", "/owner"),
                ("Setup", "/owner/setup"),
                ("Services", "/owner/services"),
                ("Availability", "/owner/availability"),
                ("Bookings", "/owner/bookings"),
                ("Invoices", "/owner/invoices"),
            ],
            owner=True,
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
