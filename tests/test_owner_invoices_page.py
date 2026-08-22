"""Owner invoice pages remain private routes with deliberate wording."""

from takdora.pages.owner_invoices import owner_invoice_detail_page, owner_invoices_page


def test_owner_invoice_components_build() -> None:
    assert owner_invoices_page() is not None
    assert owner_invoice_detail_page() is not None
