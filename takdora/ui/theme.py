"""Semantic visual tokens shared by every Takdora route."""

from __future__ import annotations

import reflex as rx

TOKENS = {
    "foreground": "#17211D",
    "muted": "#5B665F",
    "surface": "#FFFCF5",
    "surface_subtle": "#F4EFE3",
    "brand": "#A64419",
    "danger": "#B42318",
    "success": "#1D6F42",
    "warning": "#9A6700",
    "focus": "#1D6F42",
    "space_1": "0.25rem",
    "space_2": "0.5rem",
    "space_3": "0.75rem",
    "space_4": "1rem",
    "space_6": "1.5rem",
    "space_8": "2rem",
    "type_body": "1rem",
    "type_small": "0.875rem",
    "type_title": "clamp(1.75rem, 5vw, 3rem)",
    "touch_target": "2.75rem",
}


takdora_theme = rx.theme(
    appearance="light",
    accent_color="orange",
    gray_color="sand",
    radius="large",
    scaling="100%",
)


container_style = {
    "width": "100%",
    "max_width": "72rem",
    "margin_x": "auto",
    "padding_x": {"base": TOKENS["space_4"], "md": TOKENS["space_8"]},
}
