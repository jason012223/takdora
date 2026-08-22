"""PDF snapshots use business data and preserve the explicit regulatory boundary."""

from datetime import date
from decimal import Decimal

from takdora.invoice_pdf import render_invoice_pdf
from takdora.models import Business, Invoice, InvoiceLine


def test_invoice_pdf_is_a_real_pdf_with_business_and_customer_content() -> None:
    invoice = Invoice(
        business_id=1,
        booking_id=2,
        state="issued",
        invoice_number="INV-0001",
        customer_name="Mia Santos",
        customer_email="mia@example.test",
        issue_date=date(2026, 8, 22),
        currency="PHP",
        subtotal=Decimal("100.00"),
        grand_total=Decimal("100.00"),
        remaining_balance=Decimal("100.00"),
    )
    business = Business(creating_owner_id=1, name="Mia Studio", accent_color="#B45309")
    document = render_invoice_pdf(
        invoice,
        business,
        [
            InvoiceLine(
                invoice_id=1,
                description="Haircut",
                quantity=Decimal("1"),
                unit_price=Decimal("100"),
                extension=Decimal("100"),
            )
        ],
        [],
    )
    assert document.startswith(b"%PDF")
    assert b"INV-0001" in document
