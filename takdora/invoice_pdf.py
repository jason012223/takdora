"""Deterministic private A4 invoice renderer from stored invoice values."""

from __future__ import annotations

from io import BytesIO

from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen.canvas import Canvas

from takdora.invoicing import BIR_BOUNDARY
from takdora.models import Business, Invoice, InvoiceLine, InvoiceTaxLine


def _safe_color(value: str | None) -> HexColor:
    try:
        return HexColor(value or "#B45309")
    except (TypeError, ValueError):
        return HexColor("#B45309")


def render_invoice_pdf(
    invoice: Invoice, business: Business, lines: list[InvoiceLine], taxes: list[InvoiceTaxLine]
) -> bytes:
    """Render bytes directly; never publish a URL for customer financial data."""
    stream = BytesIO()
    page = Canvas(stream, pagesize=A4, invariant=True)
    page.setPageCompression(0)
    width, height = A4
    accent = _safe_color(business.accent_color)
    page.setFillColor(accent)
    page.rect(0, height - 72, width, 72, fill=1, stroke=0)
    page.setFillColor("white")
    page.setFont("Helvetica-Bold", 22)
    page.drawString(42, height - 45, business.name or "Takdora business")
    page.setFont("Helvetica-Bold", 18)
    page.drawRightString(width - 42, height - 45, "INVOICE")
    page.setFillColor("black")
    y = height - 110
    page.setFont("Helvetica-Bold", 11)
    page.drawString(42, y, invoice.invoice_number or "Invoice")
    page.setFont("Helvetica", 10)
    y -= 18
    page.drawString(42, y, f"Issued: {invoice.issue_date.isoformat()}")
    if invoice.due_date:
        page.drawString(250, y, f"Due: {invoice.due_date.isoformat()}")
    y -= 32
    page.setFont("Helvetica-Bold", 10)
    page.drawString(42, y, "Bill to")
    page.setFont("Helvetica", 10)
    y -= 15
    page.drawString(42, y, invoice.customer_name)
    y -= 15
    page.drawString(42, y, invoice.customer_email)
    y -= 25
    page.setFont("Helvetica-Bold", 10)
    page.drawString(42, y, "Description")
    page.drawRightString(width - 42, y, "Amount")
    page.line(42, y - 5, width - 42, y - 5)
    y -= 22
    page.setFont("Helvetica", 10)
    for line in lines:
        page.drawString(42, y, line.description[:72])
        page.drawRightString(width - 42, y, f"{invoice.currency} {line.extension:.2f}")
        y -= 18
    y -= 6
    for label, amount in (
        ("Subtotal", invoice.subtotal),
        *((tax.label, tax.amount) for tax in taxes),
        ("Total", invoice.grand_total),
    ):
        page.setFont("Helvetica-Bold" if label == "Total" else "Helvetica", 10)
        page.drawRightString(width - 150, y, label)
        page.drawRightString(width - 42, y, f"{invoice.currency} {amount:.2f}")
        y -= 18
    y -= 20
    page.setFont("Helvetica", 8)
    for text in (invoice.invoice_identity, invoice.notes, BIR_BOUNDARY):
        if text:
            for fragment in [text[i : i + 115] for i in range(0, len(text), 115)]:
                page.drawString(42, y, fragment)
                y -= 11
    page.save()
    return stream.getvalue()
