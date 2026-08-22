"""Minimal accessible owner account entry screens."""

from __future__ import annotations

import reflex as rx

from takdora.auth import AuthState
from takdora.ui.layouts import public_layout
from takdora.ui.primitives import feedback


def _account_form(
    title: str, submit_label: str, submit_event: rx.event.EventHandler
) -> rx.Component:
    return public_layout(
        rx.card(
            rx.vstack(
                rx.heading(title, size="7"),
                rx.text("Use your business email and a password with at least 12 characters."),
                rx.input(
                    placeholder="you@example.com",
                    type="email",
                    value=AuthState.email,
                    on_change=AuthState.set_email,
                    aria_label="Email address",
                    width="100%",
                ),
                rx.input(
                    placeholder="Password",
                    type="password",
                    value=AuthState.password,
                    on_change=AuthState.set_password,
                    aria_label="Password",
                    width="100%",
                ),
                rx.button(submit_label, on_click=submit_event, width="100%"),
                rx.cond(
                    AuthState.feedback_message != "",
                    feedback(AuthState.feedback_message, kind="error"),
                ),
                spacing="4",
                width="100%",
            ),
            max_width="30rem",
            width="100%",
        )
    )


def register_page() -> rx.Component:
    return _account_form("Create your business account", "Create account", AuthState.register)


def sign_in_page() -> rx.Component:
    return _account_form("Welcome back", "Sign in", AuthState.sign_in)
