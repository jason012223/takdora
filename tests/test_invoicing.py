"""Invoice money and privacy boundaries that do not depend on a live database."""

from decimal import Decimal

import pytest

from takdora.invoicing import BIR_BOUNDARY, calculate_totals, set_received_total


def test_calculates_decimal_invoice_totals_without_float_arithmetic() -> None:
    lines, taxes, subtotal, tax_total, total = calculate_totals(
        [{"description": "Consultation", "quantity": "1.50", "unit_price": "100.10"}],
        [{"label": "VAT", "rate": "12", "amount": "18.02"}],
    )
    assert lines[0]["extension"] == Decimal("150.15")
    assert taxes[0]["amount"] == Decimal("18.02")
    assert (subtotal, tax_total, total) == (Decimal("150.15"), Decimal("18.02"), Decimal("168.17"))


@pytest.mark.parametrize("bad", [-1, 1.2, "not-money"])
def test_rejects_unsafe_money_inputs(bad: object) -> None:
    if isinstance(bad, float):
        assert set_received_total(None, "1", bad).outcome == "validation_error"
    else:
        with pytest.raises(ValueError):
            calculate_totals([{"description": "Service", "quantity": "1", "unit_price": bad}], [])


def test_bir_boundary_never_claims_certification() -> None:
    assert "not BIR-registered" in BIR_BOUNDARY
    assert "compliant electronic invoices" in BIR_BOUNDARY
