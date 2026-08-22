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
    return rx.center(
        rx.vstack(
            rx.heading("Takdora foundation", size="8"),
            rx.text("A safe readiness check for the application database."),
            rx.button(
                "Check database readiness",
                on_click=FoundationState.run_readiness_probe,
                id="readiness-control",
            ),
            rx.text(FoundationState.probe_result, id="readiness-result", role="status"),
            spacing="4",
            align="center",
        ),
        min_height="100vh",
    )


settings = get_settings()
settings.initialize_sentry()
health_api = Starlette(routes=[Route("/healthz", health_response, methods=["GET"])])
app = rx.App(api_transformer=health_api)
app.add_page(index, route="/", title="Takdora")
