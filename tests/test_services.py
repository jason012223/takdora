"""Catalog contracts that do not require a live database connection."""

from decimal import Decimal

import pytest

from takdora.models import BusinessService
from takdora.services import ServiceInput, customer_service_projection, validate_service_input


def test_service_input_requires_a_normalized_name_and_positive_fixed_duration() -> None:
    validated = validate_service_input(ServiceInput("  Haircut  ", "60", " Neat trim ", "250"))
    assert validated.name == "Haircut"
    assert validated.fixed_duration_minutes == 60
    assert validated.price == Decimal("250.00")


@pytest.mark.parametrize(
    "data",
    [
        ServiceInput(" ", 30),
        ServiceInput("Massage", 0),
        ServiceInput("Massage", 60, price="not-money"),
        ServiceInput("Massage", 60, price="-1"),
    ],
)
def test_invalid_service_input_is_rejected_before_a_write(data: ServiceInput) -> None:
    with pytest.raises(ValueError):
        validate_service_input(data)


def test_customer_projection_uses_a_single_safe_missing_price_value() -> None:
    service = BusinessService(business_id=1, name="Haircut", fixed_duration_minutes=45)
    projection = customer_service_projection(service)
    assert projection.price_label == "Price on request"
    service.price = Decimal("350")
    assert customer_service_projection(service).price_label == "₱350.00"


def test_inactive_service_cannot_be_projected_for_customers() -> None:
    service = BusinessService(
        business_id=1, name="Legacy service", fixed_duration_minutes=30, is_active=False
    )
    with pytest.raises(ValueError, match="Inactive"):
        customer_service_projection(service)
