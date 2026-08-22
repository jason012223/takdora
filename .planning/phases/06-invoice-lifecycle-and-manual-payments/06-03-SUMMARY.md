---
phase: 06-invoice-lifecycle-and-manual-payments
plan: 03
subsystem: payments
tags: [decimal, smtp, outbox, invoice]
requires:
  - phase: 06-invoice-lifecycle-and-manual-payments
    provides: frozen issued invoice records and server-held PDFs
provides:
  - received-total manual payment status transition
  - explicit post-commit invoice-email outbox delivery
affects: [07-reliability-and-launch-hardening]
actuals:
  tokens: 5400
  tasks: 2
  commits: 1
tech-stack:
  added: []
  patterns: [committed-outbox dispatch, server-held PDF attachment]
key-files:
  created: [takdora/invoice_notifications.py]
  modified: [takdora/mailer.py, takdora/invoicing.py]
key-decisions:
  - "Owners enter one received total; v1 stores no payment ledger or provider details."
  - "PDF and payment emails are explicit actions and delivery failure cannot reverse finance data."
requirements-completed: [INV-06, INV-07]
coverage:
  - id: D1
    description: Decimal manual payment state and optional email copy
    requirement: INV-06
    verification:
      - kind: unit
        ref: tests/test_invoicing.py, tests/test_invoice_notifications.py
        status: pass
    human_judgment: false
duration: 18min
completed: 2026-08-22
status: complete
---

# Phase 6 Plan 03: Manual Payments and Email Summary

**Owners can record one exact received total, see clear payment states, and deliberately send server-held invoice PDFs or payment updates.**

## Accomplishments

- Added outstanding, partially paid, paid, and void transitions from one received-total value.
- Added idempotent invoice email outbox records and attachment-capable SMTP messages.
- Kept failed delivery retryable without rolling back issued or payment data.

## Task Commits

1. **Tasks 1–2: payment states and intentional delivery** — `05f7d1b`

## Decisions Made

- Invoice email recipients and attachment bytes are always derived from frozen server records.

## Deviations from Plan

### Deferred Existing Failure

- `tests/test_ui_layouts.py::test_dialog_and_calendar_are_reusable_and_privacy_safe` fails because an unrelated pre-existing expected source phrase is absent from `takdora/ui/primitives.py`; Phase 6 did not modify that file.

## Next Phase Readiness

Phase 7 can add delivery retry UX and durable production document storage without changing authorization rules.

## Self-Check: PASSED
