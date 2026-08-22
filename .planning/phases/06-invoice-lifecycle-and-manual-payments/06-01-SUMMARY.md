---
phase: 06-invoice-lifecycle-and-manual-payments
plan: 01
subsystem: invoices
tags: [reflex, sqlmodel, decimal, tenancy]
requires:
  - phase: 05-owner-booking-operations
    provides: completed owner-authorized bookings
provides:
  - completed-booking-only editable invoice drafts
  - tenant-scoped exact decimal draft calculations
affects: [06-02, 06-03]
actuals:
  tokens: 11500
  tasks: 2
  commits: 1
tech-stack:
  added: []
  patterns: [owner-derived workspace authorization, Decimal-only financial commands]
key-files:
  created: [takdora/invoicing.py, takdora/pages/owner_invoices.py]
  modified: [takdora/models.py, takdora/pages/owner_bookings.py]
key-decisions:
  - "Drafts can originate only from completed bookings and are never blank entries."
  - "Money is normalized and persisted as Decimal before any total is calculated."
requirements-completed: [INV-01, INV-02, INV-03]
coverage:
  - id: D1
    description: Completed-booking invoice draft and exact draft total logic
    requirement: INV-01
    verification:
      - kind: unit
        ref: tests/test_invoicing.py
        status: pass
    human_judgment: false
duration: 35min
completed: 2026-08-22
status: complete
---

# Phase 6 Plan 01: Invoice Drafts Summary

**Tenant-scoped drafts now start only from completed bookings, copy customer/service data, and use Decimal-only editable totals.**

## Accomplishments

- Added invoice, lines, configurable tax lines, and sequence persistence models.
- Added protected owner draft command and a concise Reflex editor route.
- Added booking-detail Create invoice entry point and BIR boundary wording.

## Task Commits

1. **Tasks 1–2: completed booking draft and exact draft edits** — `9a24d26`

## Decisions Made

- A missing booked-service price becomes a quote-ready `0.00` line; the owner must validate it before issue.
- Foreign or ineligible IDs resolve to bounded not-found/state outcomes.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Framework] Avoided a Reflex dynamic-route state-name collision.**
- **Fix:** Used `selected_invoice_id` rather than shadowing the `invoice_id` route argument.
- **Verification:** focused invoice tests pass.

## Issues Encountered

None in the focused invoice checks.

## Next Phase Readiness

Draft records supply the immutable issue and PDF inputs.

## Self-Check: PASSED
