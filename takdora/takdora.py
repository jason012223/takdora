"""Takdora Reflex application and its deliberately small readiness tracer."""

from __future__ import annotations

import reflex as rx
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from sqlmodel import select
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, RedirectResponse
from starlette.routing import Route

from takdora.auth import AuthState, resolve_session_owner
from takdora.config import get_settings
from takdora.documents import DocumentStorageError, presigned_download
from takdora.models import Invoice, InvoiceDocument, record_probe
from takdora.pages.auth import register_page, request_reset_page, reset_password_page, sign_in_page
from takdora.pages.availability import AvailabilityState, availability_page
from takdora.pages.design_system import design_system
from takdora.pages.marketing import features_page, help_page, home_page, portfolio_page
from takdora.pages.onboarding import onboarding_page
from takdora.pages.owner_bookings import OwnerBookingsState, owner_bookings_page
from takdora.pages.owner_dashboard import OwnerDashboardState, owner_dashboard
from takdora.pages.owner_invoices import (
    OwnerInvoicesState,
    owner_invoice_detail_page,
    owner_invoices_page,
)
from takdora.pages.public_booking import PublicBookingState, privacy_page, public_booking_page
from takdora.pages.services import ServicesState, services_page
from takdora.pages.ui_preview import ui_preview
from takdora.tenancy import get_workspace_for_owner
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


def private_document_response(request: Request) -> RedirectResponse | JSONResponse:
    """Do not enumerate documents: unauthenticated and foreign requests look identical."""
    owner = resolve_session_owner(request.cookies.get("takdora_session", ""))
    try:
        invoice_id = int(request.path_params["invoice_id"])
        business = get_workspace_for_owner(owner)
    except (TypeError, ValueError):
        return JSONResponse({"detail": "Not found."}, status_code=404)
    if owner is None or business is None:
        return JSONResponse({"detail": "Not found."}, status_code=404)
    with rx.session() as session:
        invoice = session.exec(
            select(Invoice).where(Invoice.id == invoice_id, Invoice.business_id == business.id)
        ).first()
        document = (
            session.exec(
                select(InvoiceDocument).where(InvoiceDocument.invoice_id == invoice.id)
            ).first()
            if invoice and invoice.state == "issued"
            else None
        )
    if document is None or not document.storage_key:
        return JSONResponse({"detail": "Not found."}, status_code=404)
    try:
        return RedirectResponse(
            presigned_download(
                get_settings(), key=document.storage_key, filename=document.filename
            ),
            status_code=307,
        )
    except DocumentStorageError:
        return JSONResponse({"detail": "Not found."}, status_code=404)


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
health_api = Starlette(
    routes=[
        Route("/healthz", health_response, methods=["GET"]),
        Route("/documents/{invoice_id:int}", private_document_response, methods=["GET"]),
    ]
)
app = rx.App(
    api_transformer=health_api,
    theme=takdora_theme,
    stylesheets=["/takdora.css"],
)
app.add_page(home_page, route="/", title="Takdora | Booking and invoices")
app.add_page(features_page, route="/features", title="Takdora features")
app.add_page(help_page, route="/help", title="Takdora help")
app.add_page(portfolio_page, route="/portfolio", title="Explore Takdora")
app.add_page(design_system, route="/design-system", title="Takdora interface patterns")
app.add_page(ui_preview, route="/ui-preview", title="Takdora responsive UI preview")
app.add_page(register_page, route="/register", title="Create your Takdora account")
app.add_page(sign_in_page, route="/sign-in", title="Sign in to Takdora")
app.add_page(
    owner_dashboard,
    route="/owner",
    title="Your Takdora workspace",
    on_load=OwnerDashboardState.load_dashboard,
)
app.add_page(
    owner_bookings_page,
    route="/owner/bookings",
    title="Manage bookings",
    on_load=OwnerBookingsState.load_bookings,
)
app.add_page(
    owner_invoices_page,
    route="/owner/invoices",
    title="Manage invoices",
    on_load=OwnerInvoicesState.load_list,
)
app.add_page(
    owner_invoice_detail_page,
    route="/owner/invoices/[invoice_id]",
    title="Invoice details",
    on_load=OwnerInvoicesState.load_invoice,
)
app.add_page(onboarding_page, route="/owner/setup", title="Set up your Takdora business")
app.add_page(
    services_page,
    route="/owner/services",
    title="Manage services",
    on_load=ServicesState.load_services,
)
app.add_page(
    availability_page,
    route="/owner/availability",
    title="Set availability",
    on_load=AvailabilityState.load_availability,
)
app.add_page(
    public_booking_page,
    route="/b/[business_slug]",
    title="Book with Takdora",
    on_load=PublicBookingState.load_public_page,
)
app.add_page(privacy_page, route="/privacy", title="Takdora privacy")
app.add_page(request_reset_page, route="/request-reset", title="Reset your Takdora password")
app.add_page(
    reset_password_page,
    route="/reset-password",
    title="Choose a new Takdora password",
    on_load=AuthState.capture_reset_token,
)
