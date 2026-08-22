"""Tenant-safe invoice commands; all monetary values stay Decimal server-side."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation

import reflex as rx
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from takdora.models import (
    Booking,
    Business,
    BusinessService,
    Invoice,
    InvoiceDocument,
    InvoiceEmailOutbox,
    InvoiceLine,
    InvoiceSequence,
    InvoiceTaxLine,
    OwnerAccount,
)
from takdora.tenancy import WorkspaceAccessError, get_workspace_for_owner, require_owner

MONEY_PLACES = Decimal("0.01")
MAX_LINES = 20
MAX_TAX_LINES = 5
BIR_BOUNDARY = (
    "Takdora invoices are configurable records and are not BIR-registered or compliant "
    "electronic invoices, sales-reporting filings, or a tax determination."
)


@dataclass(frozen=True)
class InvoiceResult:
    outcome: str
    message: str
    invoice_id: int | None = None


@dataclass(frozen=True)
class InvoiceProjection:
    id: int
    state: str
    payment_status: str
    invoice_number: str
    customer_name: str
    customer_email: str
    currency: str
    subtotal: Decimal
    tax_total: Decimal
    grand_total: Decimal
    received_total: Decimal
    remaining_balance: Decimal
    issue_date: date
    due_date: date | None
    notes: str
    invoice_identity: str
    lines: tuple[dict[str, str], ...]
    taxes: tuple[dict[str, str], ...]


def _business_for_owner(owner: OwnerAccount | None) -> Business:
    return get_workspace_for_owner(require_owner(owner)) or (_ for _ in ()).throw(
        WorkspaceAccessError("Invoice not found.")
    )


def _money(value: object, *, allow_zero: bool = True) -> Decimal:
    if isinstance(value, float):
        raise ValueError("Enter an exact amount with up to two decimal places.")
    try:
        amount = Decimal(str(value).strip())
    except (AttributeError, InvalidOperation, ValueError) as error:
        raise ValueError("Enter a valid amount.") from error
    if not amount.is_finite() or amount < 0 or (not allow_zero and amount == 0):
        raise ValueError("Enter an amount greater than zero.")
    return amount.quantize(MONEY_PLACES, rounding=ROUND_HALF_UP)


def _quantity(value: object) -> Decimal:
    amount = _money(value, allow_zero=False)
    if amount > Decimal("999999.99"):
        raise ValueError("Quantity is too large.")
    return amount


def _date(value: object, *, required: bool = False) -> date | None:
    if value in (None, ""):
        return date.today() if required else None
    try:
        return date.fromisoformat(str(value))
    except ValueError as error:
        raise ValueError("Enter a valid date.") from error


def _text(value: object, field: str, maximum: int, *, required: bool = False) -> str:
    text = str(value or "").strip()
    if required and not text:
        raise ValueError(f"Enter {field}.")
    if len(text) > maximum:
        raise ValueError(f"Keep {field} under {maximum} characters.")
    return text


def calculate_totals(
    lines: list[dict[str, object]], taxes: list[dict[str, object]]
) -> tuple[
    list[dict[str, Decimal | str]], list[dict[str, Decimal | str | None]], Decimal, Decimal, Decimal
]:
    """Normalize bounded input and return exact persisted calculations."""
    if not lines or len(lines) > MAX_LINES or len(taxes) > MAX_TAX_LINES:
        raise ValueError("Use between one and twenty lines and up to five tax lines.")
    normalized_lines: list[dict[str, Decimal | str]] = []
    subtotal = Decimal("0.00")
    for line in lines:
        description = _text(line.get("description"), "a line description", 500, required=True)
        quantity = _quantity(line.get("quantity"))
        unit_price = _money(line.get("unit_price"))
        extension = (quantity * unit_price).quantize(MONEY_PLACES, rounding=ROUND_HALF_UP)
        normalized_lines.append(
            {
                "description": description,
                "quantity": quantity,
                "unit_price": unit_price,
                "extension": extension,
            }
        )
        subtotal += extension
    normalized_taxes: list[dict[str, Decimal | str | None]] = []
    tax_total = Decimal("0.00")
    for tax in taxes:
        label = _text(tax.get("label"), "a tax label", 80, required=True)
        raw_rate = tax.get("rate")
        rate = None if raw_rate in (None, "") else _money(raw_rate)
        amount = _money(tax.get("amount"))
        normalized_taxes.append({"label": label, "rate": rate, "amount": amount})
        tax_total += amount
    subtotal = subtotal.quantize(MONEY_PLACES)
    tax_total = tax_total.quantize(MONEY_PLACES)
    return (
        normalized_lines,
        normalized_taxes,
        subtotal,
        tax_total,
        (subtotal + tax_total).quantize(MONEY_PLACES),
    )


def _projection(session: rx.Model, invoice: Invoice) -> InvoiceProjection:
    lines = session.exec(select(InvoiceLine).where(InvoiceLine.invoice_id == invoice.id)).all()
    taxes = session.exec(
        select(InvoiceTaxLine).where(InvoiceTaxLine.invoice_id == invoice.id)
    ).all()
    return InvoiceProjection(
        id=invoice.id or 0,
        state=invoice.state,
        payment_status=invoice.payment_status,
        invoice_number=invoice.invoice_number or "Draft",
        customer_name=invoice.customer_name,
        customer_email=invoice.customer_email,
        currency=invoice.currency,
        subtotal=invoice.subtotal,
        tax_total=invoice.tax_total,
        grand_total=invoice.grand_total,
        received_total=invoice.received_total,
        remaining_balance=invoice.remaining_balance,
        issue_date=invoice.issue_date,
        due_date=invoice.due_date,
        notes=invoice.notes,
        invoice_identity=invoice.invoice_identity,
        lines=tuple(
            {
                "description": x.description,
                "quantity": str(x.quantity),
                "unit_price": str(x.unit_price),
            }
            for x in lines
        ),
        taxes=tuple(
            {"label": x.label, "rate": str(x.rate or ""), "amount": str(x.amount)} for x in taxes
        ),
    )


def start_invoice_draft(owner: OwnerAccount | None, booking_id: int | str) -> InvoiceResult:
    """Create one draft only from an owned completed booking, never a blank invoice."""
    try:
        business = _business_for_owner(owner)
        record_id = int(booking_id)
    except (WorkspaceAccessError, TypeError, ValueError):
        return InvoiceResult("not_found", "Booking not found.")
    with rx.session() as session:
        booking = session.exec(
            select(Booking)
            .where(Booking.business_id == business.id, Booking.id == record_id)
            .with_for_update()
        ).first()
        if booking is None:
            return InvoiceResult("not_found", "Booking not found.")
        if booking.status != "completed":
            return InvoiceResult("invalid_state", "Only completed bookings can be invoiced.")
        existing = session.exec(
            select(Invoice).where(
                Invoice.business_id == business.id,
                Invoice.booking_id == booking.id,
                Invoice.state.in_(("draft", "issued")),
            )
        ).first()
        if existing is not None:
            return InvoiceResult(
                "already_invoiced", "This booking already has an invoice.", existing.id
            )
        service = session.get(BusinessService, booking.service_id)
        if service is None:
            return InvoiceResult("invalid_state", "The booked service is unavailable.")
        price = service.price or Decimal("0.00")
        invoice = Invoice(
            business_id=business.id or 0,
            booking_id=booking.id or 0,
            customer_name=booking.customer_name,
            customer_email=booking.customer_email,
            customer_phone=booking.customer_phone,
            invoice_identity=business.invoice_identity,
            currency=business.currency,
            subtotal=price,
            grand_total=price,
            remaining_balance=price,
        )
        session.add(invoice)
        session.flush()
        session.add(
            InvoiceLine(
                invoice_id=invoice.id or 0,
                description=service.name,
                quantity=Decimal("1"),
                unit_price=price,
                extension=price,
            )
        )
        session.commit()
        session.refresh(invoice)
        return InvoiceResult("draft_created", "Invoice draft created.", invoice.id)


def owner_invoice(owner: OwnerAccount | None, invoice_id: int | str) -> InvoiceProjection | None:
    try:
        business = _business_for_owner(owner)
        record_id = int(invoice_id)
    except (WorkspaceAccessError, TypeError, ValueError):
        return None
    with rx.session() as session:
        invoice = session.exec(
            select(Invoice).where(Invoice.business_id == business.id, Invoice.id == record_id)
        ).first()
        return _projection(session, invoice) if invoice else None


def owner_invoices(
    owner: OwnerAccount | None, payment_status: str = ""
) -> tuple[InvoiceProjection, ...]:
    business = _business_for_owner(owner)
    with rx.session() as session:
        statement = select(Invoice).where(
            Invoice.business_id == business.id, Invoice.state != "draft"
        )
        if payment_status in {"outstanding", "partially_paid", "paid", "void"}:
            statement = statement.where(Invoice.payment_status == payment_status)
        return tuple(
            _projection(session, item)
            for item in session.exec(statement.order_by(Invoice.created_at.desc())).all()
        )


def update_invoice_draft(
    owner: OwnerAccount | None, invoice_id: int | str, values: dict[str, object]
) -> InvoiceResult:
    try:
        business = _business_for_owner(owner)
        record_id = int(invoice_id)
        lines, taxes, subtotal, tax_total, total = calculate_totals(
            values.get("lines", []), values.get("taxes", [])
        )
        issue_date = _date(values.get("issue_date"), required=True)
        due_date = _date(values.get("due_date"))
        if due_date and issue_date and due_date < issue_date:
            raise ValueError("Due date cannot be before issue date.")
        customer_name = _text(values.get("customer_name"), "the customer name", 160, required=True)
        customer_email = _text(
            values.get("customer_email"), "the customer email", 254, required=True
        )
        identity = _text(values.get("invoice_identity"), "invoice details", 2000)
        notes = _text(values.get("notes"), "notes", 2000)
    except (WorkspaceAccessError, TypeError, ValueError) as error:
        return InvoiceResult("validation_error", str(error))
    with rx.session() as session:
        invoice = session.exec(
            select(Invoice)
            .where(Invoice.business_id == business.id, Invoice.id == record_id)
            .with_for_update()
        ).first()
        if invoice is None:
            return InvoiceResult("not_found", "Invoice not found.")
        if invoice.state != "draft":
            return InvoiceResult("invalid_state", "Issued invoices cannot be edited.")
        invoice.customer_name, invoice.customer_email = customer_name, customer_email
        invoice.invoice_identity, invoice.notes, invoice.issue_date, invoice.due_date = (
            identity,
            notes,
            issue_date,
            due_date,
        )
        invoice.subtotal, invoice.tax_total, invoice.grand_total = subtotal, tax_total, total
        invoice.remaining_balance, invoice.updated_at = total, datetime.now(UTC)
        for line in session.exec(
            select(InvoiceLine).where(InvoiceLine.invoice_id == invoice.id)
        ).all():
            session.delete(line)
        for tax in session.exec(
            select(InvoiceTaxLine).where(InvoiceTaxLine.invoice_id == invoice.id)
        ).all():
            session.delete(tax)
        for line in lines:
            session.add(InvoiceLine(invoice_id=invoice.id or 0, **line))
        for tax in taxes:
            session.add(InvoiceTaxLine(invoice_id=invoice.id or 0, **tax))
        session.add(invoice)
        session.commit()
    return InvoiceResult("saved", "Invoice draft saved.", record_id)


def set_received_total(
    owner: OwnerAccount | None, invoice_id: int | str, received_total: object
) -> InvoiceResult:
    try:
        business = _business_for_owner(owner)
        record_id = int(invoice_id)
        received = _money(received_total)
    except (WorkspaceAccessError, TypeError, ValueError) as error:
        return InvoiceResult("validation_error", str(error))
    with rx.session() as session:
        invoice = session.exec(
            select(Invoice)
            .where(Invoice.business_id == business.id, Invoice.id == record_id)
            .with_for_update()
        ).first()
        if invoice is None:
            return InvoiceResult("not_found", "Invoice not found.")
        if invoice.state != "issued" or invoice.payment_status == "void":
            return InvoiceResult("invalid_state", "This invoice cannot be updated.")
        if received > invoice.grand_total:
            return InvoiceResult(
                "validation_error", "Received total cannot exceed the invoice total."
            )
        invoice.received_total = received
        invoice.remaining_balance = (invoice.grand_total - received).quantize(MONEY_PLACES)
        invoice.payment_status = (
            "outstanding"
            if received == 0
            else "paid"
            if received == invoice.grand_total
            else "partially_paid"
        )
        invoice.payment_updated_at = datetime.now(UTC)
        session.add(invoice)
        session.commit()
    return InvoiceResult("payment_updated", "Payment status updated.", record_id)


def issue_invoice(owner: OwnerAccount | None, invoice_id: int | str) -> InvoiceResult:
    """Freeze draft fields and generated bytes in one database transaction."""
    try:
        business = _business_for_owner(owner)
        record_id = int(invoice_id)
    except (WorkspaceAccessError, TypeError, ValueError):
        return InvoiceResult("not_found", "Invoice not found.")
    with rx.session() as session:
        invoice = session.exec(
            select(Invoice)
            .where(Invoice.business_id == business.id, Invoice.id == record_id)
            .with_for_update()
        ).first()
        if invoice is None:
            return InvoiceResult("not_found", "Invoice not found.")
        if invoice.state == "issued":
            return InvoiceResult("issued", "Invoice already issued.", invoice.id)
        if invoice.state != "draft":
            return InvoiceResult("invalid_state", "This invoice cannot be issued.")
        lines = session.exec(select(InvoiceLine).where(InvoiceLine.invoice_id == invoice.id)).all()
        taxes = session.exec(
            select(InvoiceTaxLine).where(InvoiceTaxLine.invoice_id == invoice.id)
        ).all()
        try:
            _, _, subtotal, tax_total, total = calculate_totals(
                [
                    {
                        "description": x.description,
                        "quantity": x.quantity,
                        "unit_price": x.unit_price,
                    }
                    for x in lines
                ],
                [{"label": x.label, "rate": x.rate, "amount": x.amount} for x in taxes],
            )
        except ValueError as error:
            return InvoiceResult("validation_error", str(error))
        sequence = session.exec(
            select(InvoiceSequence)
            .where(InvoiceSequence.business_id == business.id)
            .with_for_update()
        ).first()
        if sequence is None:
            sequence = InvoiceSequence(business_id=business.id or 0)
            session.add(sequence)
            session.flush()
        number = f"INV-{sequence.next_number:04d}"
        sequence.next_number += 1
        invoice.invoice_number, invoice.state, invoice.issued_at = (
            number,
            "issued",
            datetime.now(UTC),
        )
        invoice.subtotal, invoice.tax_total, invoice.grand_total = subtotal, tax_total, total
        invoice.remaining_balance, invoice.payment_status = total, "outstanding"
        from takdora.invoice_pdf import render_invoice_pdf

        pdf = render_invoice_pdf(invoice, business, lines, taxes)
        session.add(sequence)
        session.add(invoice)
        session.flush()
        session.add(
            InvoiceDocument(invoice_id=invoice.id or 0, content=pdf, filename=f"{number}.pdf")
        )
        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            return InvoiceResult("issue_failed", "Could not issue the invoice. Please try again.")
    return InvoiceResult("issued", "Invoice issued.", record_id)


def private_invoice_document(
    owner: OwnerAccount | None, invoice_id: int | str
) -> tuple[bytes, str] | None:
    try:
        business = _business_for_owner(owner)
        record_id = int(invoice_id)
    except (WorkspaceAccessError, TypeError, ValueError):
        return None
    with rx.session() as session:
        invoice = session.exec(
            select(Invoice).where(
                Invoice.business_id == business.id,
                Invoice.id == record_id,
                Invoice.state == "issued",
            )
        ).first()
        document = (
            session.exec(
                select(InvoiceDocument).where(InvoiceDocument.invoice_id == invoice.id)
            ).first()
            if invoice
            else None
        )
        return (document.content, document.filename) if document else None


def void_and_redraft(owner: OwnerAccount | None, invoice_id: int | str) -> InvoiceResult:
    try:
        business = _business_for_owner(owner)
        record_id = int(invoice_id)
    except (WorkspaceAccessError, TypeError, ValueError):
        return InvoiceResult("not_found", "Invoice not found.")
    with rx.session() as session:
        invoice = session.exec(
            select(Invoice)
            .where(Invoice.business_id == business.id, Invoice.id == record_id)
            .with_for_update()
        ).first()
        if invoice is None:
            return InvoiceResult("not_found", "Invoice not found.")
        if invoice.state != "issued" or invoice.payment_status == "void":
            return InvoiceResult("invalid_state", "This invoice cannot be voided.")
        invoice.payment_status, invoice.voided_at = "void", datetime.now(UTC)
        session.add(invoice)
        session.flush()
        replacement = Invoice(
            business_id=business.id or 0,
            booking_id=invoice.booking_id,
            customer_name=invoice.customer_name,
            customer_email=invoice.customer_email,
            customer_phone=invoice.customer_phone,
            invoice_identity=invoice.invoice_identity,
            issue_date=invoice.issue_date,
            due_date=invoice.due_date,
            notes=invoice.notes,
            currency=invoice.currency,
            subtotal=invoice.subtotal,
            tax_total=invoice.tax_total,
            grand_total=invoice.grand_total,
            remaining_balance=invoice.grand_total,
        )
        session.add(replacement)
        session.flush()
        for line in session.exec(
            select(InvoiceLine).where(InvoiceLine.invoice_id == invoice.id)
        ).all():
            session.add(
                InvoiceLine(
                    invoice_id=replacement.id or 0,
                    description=line.description,
                    quantity=line.quantity,
                    unit_price=line.unit_price,
                    extension=line.extension,
                )
            )
        for tax in session.exec(
            select(InvoiceTaxLine).where(InvoiceTaxLine.invoice_id == invoice.id)
        ).all():
            session.add(
                InvoiceTaxLine(
                    invoice_id=replacement.id or 0,
                    label=tax.label,
                    rate=tax.rate,
                    amount=tax.amount,
                )
            )
        session.commit()
        return InvoiceResult("voided", "Invoice voided and a new draft created.", replacement.id)


def queue_invoice_email(
    owner: OwnerAccount | None, invoice_id: int | str, message_type: str
) -> InvoiceResult:
    try:
        business = _business_for_owner(owner)
        record_id = int(invoice_id)
    except (WorkspaceAccessError, TypeError, ValueError):
        return InvoiceResult("not_found", "Invoice not found.")
    if message_type not in {"issued_pdf", "payment_update"}:
        return InvoiceResult("validation_error", "Choose a valid email action.")
    with rx.session() as session:
        invoice = session.exec(
            select(Invoice).where(
                Invoice.business_id == business.id,
                Invoice.id == record_id,
                Invoice.state == "issued",
            )
        ).first()
        if invoice is None:
            return InvoiceResult("not_found", "Invoice not found.")
        record = session.exec(
            select(InvoiceEmailOutbox).where(
                InvoiceEmailOutbox.invoice_id == invoice.id,
                InvoiceEmailOutbox.message_type == message_type,
            )
        ).first()
        if record is None:
            session.add(
                InvoiceEmailOutbox(
                    business_id=business.id or 0,
                    invoice_id=invoice.id or 0,
                    message_type=message_type,
                    recipient_email=invoice.customer_email,
                )
            )
            session.commit()
            record = session.exec(
                select(InvoiceEmailOutbox).where(
                    InvoiceEmailOutbox.invoice_id == invoice.id,
                    InvoiceEmailOutbox.message_type == message_type,
                )
            ).first()
    if record is None:
        return InvoiceResult(
            "delivery_delayed", "Invoice email is delayed. Please try again shortly."
        )
    # Delivery is deliberately outside the committed financial transaction.
    from takdora.invoice_notifications import dispatch_invoice_email

    outcome = dispatch_invoice_email(record.id or 0)
    message = (
        "Invoice email sent."
        if outcome == "sent"
        else "Invoice email is delayed. Please try again shortly."
    )
    return InvoiceResult(
        "email_sent" if outcome == "sent" else "delivery_delayed", message, record_id
    )
