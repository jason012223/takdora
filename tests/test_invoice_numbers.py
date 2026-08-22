"""Invoice-number allocation stays safe when seeded records already exist."""

from takdora.invoicing import _next_invoice_number


def test_invoice_number_skips_numbers_already_issued_before_sequence_setup() -> None:
    number, following = _next_invoice_number(1, {"INV-0001", "INV-0002"})

    assert number == "INV-0003"
    assert following == 4


def test_invoice_number_uses_the_sequence_when_that_number_is_free() -> None:
    number, following = _next_invoice_number(8, {"INV-0001"})

    assert number == "INV-0008"
    assert following == 9
