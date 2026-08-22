"""Takdora Reflex application and its deliberately small readiness tracer."""

from __future__ import annotations

import reflex as rx
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from takdora.config import get_settings
from takdora.models import record_probe
from takdora.pages.auth import register_page, sign_in_page
from takdora.pages.design_system import design_system
from takdora.pages.ui_preview import ui_preview
from takdora.ui.shell import application_shell
from takdora.ui.theme import TOKENS, takdora_theme


class FoundationState(rx.State):
    """State for the non-sensitive foundation diagnostic."""

    probe_result: str = ""

    def run_readiness_probe(self) -> None:
        """Write and read a server-generated row without accepting browser data."""
        try:
            probe = record_probe()
        except OperationalError:
            self.probe_result = "Database is temporarily unavailable. Please try again shortly."
        else:
            self.probe_result = f"Database readiness confirmed (probe #{probe.id})."


def health_response(_request: Request | None = None) -> JSONResponse:
    """Return a bounded, credential-free PostgreSQL readiness response."""
    try:
        with rx.session() as session:
            session.execute(text("SELECT 1"))
    except OperationalError:
        return JSONResponse({"status": "unavailable"}, status_code=503)
    return JSONResponse({"status": "ok"})


def index() -> rx.Component:
    return application_shell(
        rx.vstack(
            rx.badge("Takdora foundation", color_scheme="orange", variant="soft"),
            rx.heading(
                "A dependable start for your business.", size="8", color=TOKENS["foreground"]
            ),
            rx.text(
                "This safe readiness check confirms the Takdora application database is available.",
                color=TOKENS["muted"],
            ),
            rx.button(
                "Check database readiness",
                on_click=FoundationState.run_readiness_probe,
                id="readiness-control",
                min_height=TOKENS["touch_target"],
            ),
            rx.text(FoundationState.probe_result, id="readiness-result", role="status"),
            spacing="4",
            align="start",
            max_width="38rem",
        ),
    )


settings = get_settings()
settings.initialize_sentry()
health_api = Starlette(routes=[Route("/healthz", health_response, methods=["GET"])])
app = rx.App(api_transformer=health_api, theme=takdora_theme, stylesheets=["/takdora.css"])
app.add_page(index, route="/", title="Takdora")
app.add_page(design_system, route="/design-system", title="Takdora interface patterns")
app.add_page(ui_preview, route="/ui-preview", title="Takdora responsive UI preview")
app.add_page(register_page, route="/register", title="Create your Takdora account")
app.add_page(sign_in_page, route="/sign-in", title="Sign in to Takdora")
