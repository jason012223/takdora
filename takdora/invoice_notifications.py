"""Post-commit customer-safe delivery for explicit invoice actions."""

from __future__ import annotations

from datetime import UTC, datetime

import reflex as rx
from sqlmodel import select

from takdora.config import get_settings
from takdora.invoicing import BIR_BOUNDARY
from takdora.mailer import MailDeliveryError, Mailer
from takdora.models import Business, Invoice, InvoiceDocument, InvoiceEmailOutbox


def render_invoice_email(
    invoice: Invoice, business: Business, message_type: str
) -> tuple[str, str]:
    """Render no public link and no compliance claim from committed invoice data."""
    contact = business.contact_email or business.contact_phone or "the business directly"
    subject = f"Invoice {invoice.invoice_number} from {business.name}"
    if message_type == "payment_update":
        payment_label = invoice.payment_status.replace("_", " ")
        body = (
            f"Your invoice {invoice.invoice_number} payment status is {payment_label}.\n\n"
            f"Amount received: {invoice.currency} {invoice.received_total:.2f}\n"
            f"Remaining balance: {invoice.currency} {invoice.remaining_balance:.2f}\n\n"
            f"Questions? Contact {contact}.\n\n{BIR_BOUNDARY}"
        )
    else:
        body = (
            f"Your invoice {invoice.invoice_number} is attached.\n\n"
            f"Total: {invoice.currency} {invoice.grand_total:.2f}\n"
            f"Questions? Contact {contact}.\n\n{BIR_BOUNDARY}"
        )
    return subject, body


def dispatch_invoice_email(outbox_id: int, *, mailer: Mailer | None = None) -> str:
    """Try one persisted request; failure never mutates financial state."""
    with rx.session() as session:
        outbox = session.get(InvoiceEmailOutbox, outbox_id)
        if outbox is None:
            return "missing"
        if outbox.delivery_status == "sent":
            return "sent"
        invoice = session.get(Invoice, outbox.invoice_id)
        business = session.get(Business, outbox.business_id)
        document = session.exec(
            select(InvoiceDocument).where(InvoiceDocument.invoice_id == outbox.invoice_id)
        ).first()
        if invoice is None or business is None or document is None or invoice.state != "issued":
            outbox.delivery_status, outbox.last_error = "delayed", "invoice_data_unavailable"
            outbox.updated_at = datetime.now(UTC)
            session.add(outbox)
            session.commit()
            return "delayed"
        subject, body = render_invoice_email(invoice, business, outbox.message_type)
        outbox.attempts += 1
        session.add(outbox)
        session.commit()
    try:
        (mailer or Mailer(get_settings())).send_invoice_email(
            outbox.recipient_email,
            subject,
            body,
            pdf=document.content if outbox.message_type == "issued_pdf" else None,
            filename=document.filename,
        )
    except MailDeliveryError:
        with rx.session() as session:
            stored = session.get(InvoiceEmailOutbox, outbox.id)
            if stored:
                stored.delivery_status, stored.last_error, stored.updated_at = (
                    "delayed",
                    "mail_delivery_failed",
                    datetime.now(UTC),
                )
                session.add(stored)
                session.commit()
        return "delayed"
    with rx.session() as session:
        stored = session.get(InvoiceEmailOutbox, outbox.id)
        if stored:
            stored.delivery_status, stored.last_error, stored.sent_at, stored.updated_at = (
                "sent",
                None,
                datetime.now(UTC),
                datetime.now(UTC),
            )
            session.add(stored)
            session.commit()
    return "sent"
