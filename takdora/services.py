"""Tenant-safe service catalog commands and customer-safe projections."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation

import reflex as rx
from sqlmodel import select

from takdora.models import Business, BusinessService, OwnerAccount
from takdora.tenancy import WorkspaceAccessError, get_workspace_for_owner, require_owner

MAX_DESCRIPTION_LENGTH = 1000
MONEY_QUANTUM = Decimal("0.01")


@dataclass(frozen=True)
class ServiceInput:
    name: str
    fixed_duration_minutes: int | str
    description: str = ""
    price: str | Decimal | None = None


@dataclass(frozen=True)
class CustomerService:
    """Only fields that later public booking pages may safely render."""

    id: int
    name: str
    duration_label: str
    price_label: str


def validate_service_input(data: ServiceInput) -> ServiceInput:
    name = data.name.strip()
    if not name:
        raise ValueError("Service name is required.")
    if len(name) > 120:
        raise ValueError("Service name must be 120 characters or fewer.")
    try:
        duration = int(data.fixed_duration_minutes)
    except (TypeError, ValueError) as error:
        raise ValueError("Choose a positive fixed duration.") from error
    if duration <= 0 or duration > 720:
        raise ValueError("Choose a fixed duration between 1 and 720 minutes.")
    description = data.description.strip()
    if len(description) > MAX_DESCRIPTION_LENGTH:
        raise ValueError("Description must be 1,000 characters or fewer.")
    price: Decimal | None = None
    if data.price not in (None, ""):
        try:
            price = Decimal(str(data.price)).quantize(MONEY_QUANTUM, rounding=ROUND_HALF_UP)
        except (InvalidOperation, ValueError) as error:
            raise ValueError("Enter a valid price.") from error
        if not price.is_finite() or price < 0 or price > Decimal("9999999999.99"):
            raise ValueError("Enter a valid non-negative price.")
    return ServiceInput(
        name=name, fixed_duration_minutes=duration, description=description, price=price
    )


def _authorized_business(owner: OwnerAccount | None) -> Business:
    authorized_owner = require_owner(owner)
    business = get_workspace_for_owner(authorized_owner)
    if business is None:
        raise WorkspaceAccessError("Workspace not found.")
    return business


def create_service(owner: OwnerAccount | None, data: ServiceInput) -> BusinessService:
    """Create a service only in the authenticated owner's resolved workspace."""
    business = _authorized_business(owner)
    validated = validate_service_input(data)
    with rx.session() as session:
        service = BusinessService(
            business_id=business.id or 0,
            name=validated.name,
            fixed_duration_minutes=int(validated.fixed_duration_minutes),
            description=validated.description or None,
            price=validated.price,
        )
        session.add(service)
        session.commit()
        session.refresh(service)
        return service


def edit_service(
    owner: OwnerAccount | None, service_id: int, data: ServiceInput
) -> BusinessService:
    business = _authorized_business(owner)
    validated = validate_service_input(data)
    with rx.session() as session:
        service = session.get(BusinessService, service_id)
        if service is None or service.business_id != business.id:
            raise WorkspaceAccessError("Service not found.")
        service.name = validated.name
        service.fixed_duration_minutes = int(validated.fixed_duration_minutes)
        service.description = validated.description or None
        service.price = validated.price
        service.updated_at = datetime.now(UTC)
        session.add(service)
        session.commit()
        session.refresh(service)
        return service


def set_service_active(
    owner: OwnerAccount | None, service_id: int, *, active: bool
) -> BusinessService:
    business = _authorized_business(owner)
    with rx.session() as session:
        service = session.get(BusinessService, service_id)
        if service is None or service.business_id != business.id:
            raise WorkspaceAccessError("Service not found.")
        service.is_active = active
        service.updated_at = datetime.now(UTC)
        session.add(service)
        session.commit()
        session.refresh(service)
        return service


def services_for_owner(owner: OwnerAccount | None) -> list[BusinessService]:
    business = _authorized_business(owner)
    with rx.session() as session:
        return list(
            session.exec(
                select(BusinessService)
                .where(BusinessService.business_id == business.id)
                .order_by(BusinessService.is_active.desc(), BusinessService.name)
            ).all()
        )


def active_services_for_business(business_id: int) -> list[BusinessService]:
    """Future public flows call this only after resolving the public business safely."""
    with rx.session() as session:
        return list(
            session.exec(
                select(BusinessService)
                .where(
                    BusinessService.business_id == business_id, BusinessService.is_active.is_(True)
                )
                .order_by(BusinessService.name)
            ).all()
        )


def active_service_present_for_business(business_id: int) -> bool:
    with rx.session() as session:
        return (
            session.exec(
                select(BusinessService.id).where(
                    BusinessService.business_id == business_id, BusinessService.is_active.is_(True)
                )
            ).first()
            is not None
        )


def customer_service_projection(
    service: BusinessService, *, currency: str = "PHP"
) -> CustomerService:
    if not service.is_active:
        raise ValueError("Inactive services cannot be displayed to customers.")
    price_label = "Price on request"
    if service.price is not None:
        symbol = "₱" if currency == "PHP" else f"{currency} "
        price_label = f"{symbol}{service.price:,.2f}"
    return CustomerService(
        id=service.id or 0,
        name=service.name,
        duration_label=f"{service.fixed_duration_minutes} minutes",
        price_label=price_label,
    )
