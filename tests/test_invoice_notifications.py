"""Customer invoice emails describe financial state without a public link."""

from decimal import Decimal

from takdora.invoice_notifications import render_invoice_email
from takdora.models import Business, Invoice


def test_payment_email_is_customer_safe_and_bir_bounded() -> None:
    invoice = Invoice(
        business_id=1,
        booking_id=2,
        state="issued",
        invoice_number="INV-0001",
        customer_name="Mia",
        customer_email="mia@example.test",
        currency="PHP",
        grand_total=Decimal("100"),
        received_total=Decimal("50"),
        remaining_balance=Decimal("50"),
        payment_status="partially_paid",
    )
    business = Business(creating_owner_id=1, name="Mia Studio", contact_email="hello@example.test")
    _subject, body = render_invoice_email(invoice, business, "payment_update")
    assert "PHP 50.00" in body
    assert "not BIR-registered" in body
    assert "http" not in body
