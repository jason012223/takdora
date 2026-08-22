"""Server-owned, resettable synthetic demo fixture for portfolio review."""

from __future__ import annotations

from datetime import UTC, datetime, time, timedelta
from decimal import Decimal

import reflex as rx
from sqlmodel import select

from takdora.auth import create_password_digest, issue_session
from takdora.config import Settings
from takdora.models import (
    Booking,
    BookingChangeOutbox,
    BookingConfirmationOutbox,
    BookingRules,
    Business,
    BusinessMembership,
    BusinessService,
    Invoice,
    InvoiceDocument,
    InvoiceEmailOutbox,
    InvoiceLine,
    InvoiceTaxLine,
    OwnerAccount,
    WeeklyAvailabilityBlock,
)

DEMO_EMAIL = "demo-owner@takdora.example"
DEMO_SLUG = "takdora-demo-studio"
DEMO_LABEL = "Synthetic demo"


class DemoUnavailable(ValueError):
    """The demo is not exposed unless an operator enables it server-side."""


def _require_enabled(settings: Settings) -> None:
    if not settings.synthetic_demo_enabled:
        raise DemoUnavailable("The synthetic demo is unavailable.")


def _delete_fixture_rows(session: rx.Model, business_id: int) -> None:
    """Delete only rows selected through the synthetic business marker."""
    invoices = session.exec(select(Invoice).where(Invoice.business_id == business_id)).all()
    for invoice in invoices:
        for line in session.exec(
            select(InvoiceLine).where(InvoiceLine.invoice_id == invoice.id)
        ).all():
            session.delete(line)
        for document in session.exec(
            select(InvoiceDocument).where(InvoiceDocument.invoice_id == invoice.id)
        ).all():
            session.delete(document)
        for tax in session.exec(
            select(InvoiceTaxLine).where(InvoiceTaxLine.invoice_id == invoice.id)
        ).all():
            session.delete(tax)
        for delivery in session.exec(
            select(InvoiceEmailOutbox).where(InvoiceEmailOutbox.invoice_id == invoice.id)
        ).all():
            session.delete(delivery)
        session.delete(invoice)
    for model in (BookingConfirmationOutbox, BookingChangeOutbox):
        for record in session.exec(select(model).where(model.business_id == business_id)).all():
            session.delete(record)
    for booking in session.exec(select(Booking).where(Booking.business_id == business_id)).all():
        session.delete(booking)
    for model in (WeeklyAvailabilityBlock, BookingRules, BusinessService, BusinessMembership):
        for record in session.exec(select(model).where(model.business_id == business_id)).all():
            session.delete(record)


def reset_synthetic_demo(settings: Settings) -> Business:
    """Idempotently restore one labelled scenario without contacting external systems."""
    _require_enabled(settings)
    with rx.session() as session:
        owner = session.exec(
            select(OwnerAccount).where(OwnerAccount.normalized_email == DEMO_EMAIL)
        ).first()
        if owner is None:
            digest, salt = create_password_digest("Synthetic-demo-owner")
            owner = OwnerAccount(
                normalized_email=DEMO_EMAIL,
                password_digest=digest,
                password_salt=salt,
                email_verified_at=datetime.now(UTC),
                is_synthetic_demo=True,
            )
            session.add(owner)
            session.flush()
        elif not owner.is_synthetic_demo:
            raise DemoUnavailable("The synthetic demo identity is unavailable.")
        for existing in session.exec(
            select(Business).where(
                Business.creating_owner_id == owner.id,
                Business.is_synthetic_demo.is_(True),
            )
        ).all():
            _delete_fixture_rows(session, existing.id or 0)
            # The membership table has an explicit foreign key but no ORM
            # relationship cascade. Flush its removal before deleting the
            # synthetic business so a reset remains repeatable.
            session.flush()
            session.delete(existing)
        session.flush()
        business = Business(
            creating_owner_id=owner.id or 0,
            name="Takdora Demo Studio",
            slug=DEMO_SLUG,
            contact_email="hello@takdora.example",
            contact_phone="Demo contact: hello@takdora.example",
            address="Synthetic example only",
            invoice_identity="Synthetic demo invoice — not a BIR-compliant e-invoice.",
            published_at=datetime.now(UTC),
            is_synthetic_demo=True,
        )
        session.add(business)
        session.flush()
        session.add(BusinessMembership(business_id=business.id or 0, owner_id=owner.id or 0))
        service = BusinessService(
            business_id=business.id or 0,
            name="Synthetic consultation",
            description="A synthetic record for portfolio review.",
            fixed_duration_minutes=60,
            price=Decimal("1500.00"),
        )
        session.add(service)
        session.add(BookingRules(business_id=business.id or 0))
        # The synthetic portfolio path must be bookable whenever it is opened,
        # including weekends, so reviewers can complete its lifecycle on any day.
        for weekday in range(7):
            session.add(
                WeeklyAvailabilityBlock(
                    business_id=business.id or 0,
                    weekday=weekday,
                    start_time=time(9),
                    end_time=time(17),
                )
            )
        session.flush()
        starts_at = datetime.now(UTC) - timedelta(days=1)
        booking = Booking(
            business_id=business.id or 0,
            service_id=service.id or 0,
            status="completed",
            customer_name="Synthetic customer",
            customer_email="synthetic-customer@takdora.example",
            starts_at=starts_at,
            ends_at=starts_at + timedelta(hours=1),
            business_timezone="Asia/Manila",
            idempotency_key="synthetic-demo-booking",
        )
        session.add(booking)
        session.flush()
        invoice = Invoice(
            business_id=business.id or 0,
            booking_id=booking.id or 0,
            state="issued",
            invoice_number="INV-0001",
            customer_name=booking.customer_name,
            customer_email=booking.customer_email,
            invoice_identity=business.invoice_identity,
            subtotal=Decimal("1500.00"),
            grand_total=Decimal("1500.00"),
            received_total=Decimal("750.00"),
            remaining_balance=Decimal("750.00"),
            payment_status="partially_paid",
            issued_at=datetime.now(UTC),
        )
        session.add(invoice)
        session.flush()
        session.add(
            InvoiceLine(
                invoice_id=invoice.id or 0,
                description=service.name,
                quantity=Decimal("1"),
                unit_price=Decimal("1500.00"),
                extension=Decimal("1500.00"),
            )
        )
        session.add(
            InvoiceDocument(
                invoice_id=invoice.id or 0,
                content=b"%PDF-1.4\n% synthetic demo only\n",
                filename="INV-0001.pdf",
            )
        )
        session.add(owner)
        session.commit()
        session.refresh(business)
        return business


def enter_synthetic_demo(settings: Settings) -> str:
    """Issue a normal opaque session for the server-derived fixture owner only."""
    _require_enabled(settings)
    reset_synthetic_demo(settings)
    with rx.session() as session:
        owner = session.exec(
            select(OwnerAccount).where(
                OwnerAccount.normalized_email == DEMO_EMAIL,
                OwnerAccount.is_synthetic_demo.is_(True),
            )
        ).first()
    if owner is None or owner.id is None:
        raise DemoUnavailable("The synthetic demo is unavailable.")
    return issue_session(owner.id)


def is_synthetic_demo_owner(owner: OwnerAccount | None) -> bool:
    return bool(owner and owner.is_synthetic_demo)
