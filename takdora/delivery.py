"""Tenant-scoped, bounded recovery for post-commit delivery work."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Literal

import reflex as rx
from sqlmodel import select

from takdora.booking_notifications import dispatch_change_update, dispatch_confirmation
from takdora.models import (
    BookingChangeOutbox,
    BookingConfirmationOutbox,
    InvoiceEmailOutbox,
    OwnerAccount,
)
from takdora.tenancy import WorkspaceAccessError, get_workspace_for_owner, require_owner

MAX_AUTOMATIC_ATTEMPTS = 5
DeliveryKind = Literal["confirmation", "booking_change", "invoice_email"]
_MODEL_BY_KIND = {
    "confirmation": BookingConfirmationOutbox,
    "booking_change": BookingChangeOutbox,
    "invoice_email": InvoiceEmailOutbox,
}


def _monitor_terminal(
    kind: DeliveryKind, record_id: int, business_id: int, error_code: str
) -> None:
    """Report only internal operational tags; never customer data or provider responses."""
    try:
        import sentry_sdk

        sentry_sdk.capture_message(
            "takdora_delivery_exhausted",
            level="error",
            scope=lambda scope: scope.set_tags(
                {
                    "delivery_kind": kind,
                    "delivery_record_id": str(record_id),
                    "business_id": str(business_id),
                    "error_code": error_code,
                }
            ),
        )
    except Exception:  # Monitoring must never block owner recovery.
        return


def _backoff(attempts: int) -> timedelta:
    return timedelta(minutes=min(60, 2 ** max(0, attempts - 1)))


def delivery_issues_for_owner(owner: OwnerAccount | None) -> list[dict[str, str | int]]:
    """Return bounded recovery data after deriving the workspace server-side."""
    business = get_workspace_for_owner(require_owner(owner))
    if business is None:
        return []
    rows: list[dict[str, str | int]] = []
    with rx.session() as session:
        for kind, model in _MODEL_BY_KIND.items():
            records = session.exec(
                select(model).where(
                    model.business_id == business.id, model.delivery_status == "delayed"
                )
            ).all()
            rows.extend(
                {
                    "id": record.id or 0,
                    "kind": kind,
                    "label": "Booking confirmation" if kind == "confirmation" else "Customer email",
                    "status": "Email delivery is delayed. Your saved record is safe.",
                }
                for record in records
                if record.terminal_at is None
            )
    return rows


def _dispatch(kind: DeliveryKind, record_id: int) -> str:
    if kind == "confirmation":
        with rx.session() as session:
            record = session.get(BookingConfirmationOutbox, record_id)
            return dispatch_confirmation(record.booking_id) if record else "missing"
    if kind == "booking_change":
        return dispatch_change_update(record_id)
    from takdora.invoice_notifications import dispatch_invoice_email

    return dispatch_invoice_email(record_id)


def retry_delivery_for_owner(owner: OwnerAccount | None, kind: DeliveryKind, record_id: int) -> str:
    """Retry one owned delivery without accepting a browser business ID or recipient."""
    if kind not in _MODEL_BY_KIND or record_id <= 0:
        raise WorkspaceAccessError("Delivery item not found.")
    business = get_workspace_for_owner(require_owner(owner))
    if business is None:
        raise WorkspaceAccessError("Delivery item not found.")
    model = _MODEL_BY_KIND[kind]
    with rx.session() as session:
        record = session.get(model, record_id)
        if record is None or record.business_id != business.id:
            raise WorkspaceAccessError("Delivery item not found.")
        if record.delivery_status == "sent":
            return "sent"
        if record.terminal_at is not None:
            return "exhausted"
        record.next_attempt_at = datetime.now(UTC)
        session.add(record)
        session.commit()
    return _finalize_attempt(kind, record_id)


def _finalize_attempt(kind: DeliveryKind, record_id: int) -> str:
    result = _dispatch(kind, record_id)
    model = _MODEL_BY_KIND[kind]
    with rx.session() as session:
        record = session.get(model, record_id)
        if record is None or result in {"sent", "missing"}:
            return result
        now = datetime.now(UTC)
        if record.attempts >= MAX_AUTOMATIC_ATTEMPTS:
            record.terminal_at = now
            record.delivery_status = "delayed"
            record.last_error = record.last_error or "delivery_attempts_exhausted"
            _monitor_terminal(kind, record.id or 0, record.business_id, record.last_error)
            session.add(record)
            session.commit()
            return "exhausted"
        record.next_attempt_at = now + _backoff(record.attempts)
        session.add(record)
        session.commit()
    return result


def process_due_deliveries(now: datetime | None = None) -> int:
    """Process due delayed records up to five attempts; terminal sent rows are skipped."""
    due_at = now or datetime.now(UTC)
    due: list[tuple[DeliveryKind, int]] = []
    with rx.session() as session:
        for kind, model in _MODEL_BY_KIND.items():
            records = session.exec(
                select(model).where(
                    model.delivery_status.in_(("pending", "delayed")),
                    model.terminal_at.is_(None),
                    model.attempts < MAX_AUTOMATIC_ATTEMPTS,
                    (model.next_attempt_at.is_(None)) | (model.next_attempt_at <= due_at),
                )
            ).all()
            due.extend((kind, record.id or 0) for record in records)
    for kind, record_id in due:
        _finalize_attempt(kind, record_id)
    return len(due)
