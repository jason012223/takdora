"""Factual public marketing pages for prospective Takdora owners."""

from __future__ import annotations

import reflex as rx

from takdora.ui.layouts import marketing_layout
from takdora.ui.theme import TOKENS

PRIMARY_CTA = "Create your business"
DEMO_CTA = "Explore the demo"
MANUAL_PAYMENT_BOUNDARY = "Payments are recorded manually in Takdora v1."
INVOICE_BOUNDARY = "Invoices are BIR-aware templates, not BIR-compliant e-invoices."
SYNTHETIC_DEMO_NOTICE = "The demo uses synthetic example records, not customer data."


def _cta_row() -> rx.Component:
    return rx.hstack(
        rx.link(
            rx.button(PRIMARY_CTA, color_scheme="orange", min_height=TOKENS["touch_target"]),
            href="/register",
        ),
        rx.link(DEMO_CTA, href="/demo", size="3", underline="always"),
        spacing="4",
        align="center",
        flex_wrap="wrap",
    )


def home_page() -> rx.Component:
    """Explain the core workflow with one unmistakable owner action."""
    return marketing_layout(
        rx.vstack(
            rx.badge("For Philippine service businesses", color_scheme="orange", variant="soft"),
            rx.heading("Booking and invoicing, in one clear place.", size="9"),
            rx.text(
                "Takdora is a configurable booking and invoice hub for Philippine service businesses. "
                "Take bookings, manage appointments, and issue invoices without losing the thread.",
                size="4",
                color=TOKENS["muted"],
                max_width="48rem",
            ),
            _cta_row(),
            rx.text(SYNTHETIC_DEMO_NOTICE, size="2", color=TOKENS["muted"]),
            spacing="5",
            align="start",
        ),
        rx.el.section(
            rx.heading("A dependable workflow", size="6"),
            rx.hstack(
                *[
                    rx.card(rx.heading(title, size="4"), rx.text(copy, color=TOKENS["muted"]))
                    for title, copy in (
                        ("1. Set up", "Add your services, hours, and business details."),
                        (
                            "2. Take bookings",
                            "Customers choose an available time on your public page.",
                        ),
                        (
                            "3. Complete and invoice",
                            "Finish work, then issue a PDF and track payment manually.",
                        ),
                    )
                ],
                spacing="4",
                flex_wrap="wrap",
                width="100%",
            ),
            id="how-it-works",
        ),
    )


def features_page() -> rx.Component:
    return marketing_layout(
        rx.heading("Features for the work you do every day", size="8"),
        rx.vstack(
            rx.heading("Public booking", size="5"),
            rx.text("Share a branded booking page with services and available times."),
            rx.heading("Owner operations", size="5"),
            rx.text("Review, reschedule, cancel, and complete appointments in one workspace."),
            rx.heading("Invoices and payment tracking", size="5"),
            rx.text("Create a PDF invoice after work is completed and record what was received."),
            rx.callout(MANUAL_PAYMENT_BOUNDARY, icon="info", color_scheme="orange"),
            rx.callout(INVOICE_BOUNDARY, icon="info", color_scheme="orange"),
            _cta_row(),
            spacing="4",
            align="start",
        ),
    )


def help_page() -> rx.Component:
    return marketing_layout(
        rx.heading("Help for owners and customers", size="8"),
        rx.vstack(
            rx.heading("Owners", size="5"),
            rx.text(
                "Create your account, set up your business, add a service, then publish your booking page."
            ),
            rx.heading("Customers", size="5"),
            rx.text(
                "Choose a service and an available time. For changes or questions, contact the business directly."
            ),
            rx.heading("Payments and invoices", size="5"),
            rx.text(f"{MANUAL_PAYMENT_BOUNDARY} {INVOICE_BOUNDARY}"),
            _cta_row(),
            spacing="4",
            align="start",
        ),
    )


def portfolio_page() -> rx.Component:
    return marketing_layout(
        rx.heading("Explore the real product flow", size="8"),
        rx.vstack(
            rx.text(
                "Portfolio reviewers can inspect a synthetic business through public booking, owner booking "
                "operations, an issued invoice, and manually tracked payment state."
            ),
            rx.callout(SYNTHETIC_DEMO_NOTICE, icon="info", color_scheme="orange"),
            rx.text("The demo is resettable and does not send messages to visitors."),
            _cta_row(),
            spacing="4",
            align="start",
        ),
    )
