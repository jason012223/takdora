"""Owner invoice pages remain private routes with deliberate, safe wording."""

from takdora.pages.owner_invoices import owner_invoice_detail_page, owner_invoices_page


def test_owner_invoice_components_build() -> None:
    assert owner_invoices_page() is not None
    rendered = str(owner_invoice_detail_page())
    assert "Customer and dates" in rendered
    assert "What you are charging for" in rendered
    assert "Ready to review" in rendered
    assert "Correction options" in rendered
    assert "BIR" in rendered
