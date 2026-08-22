"""Regression coverage for factual, evidence-led marketing copy."""

from takdora.pages import marketing


def test_marketing_copy_labels_synthetic_demo_and_v1_boundaries() -> None:
    assert "synthetic" in marketing.SYNTHETIC_DEMO_NOTICE.casefold()
    assert "manual" in marketing.MANUAL_PAYMENT_BOUNDARY.casefold()
    assert "not BIR-compliant" in marketing.INVOICE_BOUNDARY


def test_marketing_copy_does_not_contain_unsupported_evidence_categories() -> None:
    copy = " ".join(
        (
            marketing.PRIMARY_CTA,
            marketing.DEMO_CTA,
            marketing.MANUAL_PAYMENT_BOUNDARY,
            marketing.INVOICE_BOUNDARY,
            marketing.SYNTHETIC_DEMO_NOTICE,
        )
    ).casefold()
    unsupported_categories = ("testimonial", "customer logo", "₱", "pricing", "bir registered")
    assert not any(category in copy for category in unsupported_categories)
