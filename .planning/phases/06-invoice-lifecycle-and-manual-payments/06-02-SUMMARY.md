---
phase: 06-invoice-lifecycle-and-manual-payments
plan: 02
subsystem: invoices
tags: [reportlab, pdf, immutable-records, tenancy]
requires:
  - phase: 06-invoice-lifecycle-and-manual-payments
    provides: editable tenant-scoped invoice drafts
provides:
  - sequential business-scoped immutable issue records
  - server-held branded private PDFs
affects: [06-03, 07-reliability-and-launch-hardening]
actuals:
  tokens: 6400
  tasks: 2
  commits: 1
tech-stack:
  added: [reportlab]
  patterns: [private bytes download via rx.download, frozen issued document]
key-files:
  created: [takdora/invoice_pdf.py]
  modified: [pyproject.toml, uv.lock, takdora/invoicing.py]
key-decisions:
  - "A generated PDF stays server-held and is returned only after tenant authorization."
  - "The PDF visibly states Takdora is not a BIR-compliant registered e-invoicing system."
requirements-completed: [INV-04, INV-05, INV-08]
coverage:
  - id: D1
    description: Deterministic branded invoice PDF with BIR boundary
    requirement: INV-05
    verification:
      - kind: unit
        ref: tests/test_invoice_pdf.py
        status: pass
    human_judgment: false
duration: 20min
completed: 2026-08-22
status: complete
---

# Phase 6 Plan 02: Issued Invoice PDFs Summary

**Issued invoices allocate one business-local `INV-0001` sequence, freeze their values, and immediately retain an owner-authorized PDF.**

## Accomplishments

- Added locked ReportLab rendering and deterministic PDF bytes.
- Added private document records, frozen issue flow, and void-and-redraft correction path.
- Kept logo/color rendering and non-compliance wording inside the one branded template.

## Task Commits

1. **Tasks 1–2: issue, private download, and correction flow** — `7434eb3`

## Decisions Made

- Issuing is idempotent and never offers an edit/replacement route for the issued state.

## Deviations from Plan

None - plan implemented with the existing owner page as the issue/download control.

## Next Phase Readiness

Issued snapshots and document bytes are ready for intentional email delivery.

## Self-Check: PASSED
