---
phase: 04-safe-public-booking
plan: 03
subsystem: notifications-ui
tags: [outbox, smtp, reflex, playwright]
requires:
  - phase: 04-02
    provides: committed booking result and conflict contract
provides:
  - booking-linked confirmation outbox and post-commit dispatcher
  - truthful success, delayed-email, and slot-conflict recovery UI
affects: [07-reliability-and-launch-hardening, owner-booking-operations]
actuals:
  tokens: 7200
  tasks: 2
  commits: 3
tech-stack:
  added: []
  patterns: [post-commit delivery, durable delayed status, guarded browser smoke]
key-files:
  created: [takdora/booking_notifications.py, tests/e2e/test_public_booking_smoke.py]
  modified: [takdora/booking.py, takdora/mailer.py, takdora/pages/public_booking.py]
key-decisions:
  - "A committed booking remains confirmed when email delivery is delayed."
  - "Conflict recovery preserves customer fields and clears only the unavailable slot."
requirements-completed: [BOOK-06, NOTF-01]
coverage:
  - id: D1
    description: Confirmation content includes only concise customer-safe appointment data
    requirement: NOTF-01
    verification:
      - kind: unit
        ref: tests/test_booking_notifications.py
        status: pass
    human_judgment: false
  - id: D2
    description: Real-browser published booking form smoke test
    requirement: BOOK-06
    verification:
      - kind: automated_ui
        ref: tests/e2e/test_public_booking_smoke.py
        status: unknown
    human_judgment: true
    rationale: The Compose browser-port limitation prevented an honest local browser run.
duration: 31min
completed: 2026-08-22
status: complete
---

# Phase 04 Plan 03: Truthful customer outcome and confirmation Summary

**Durable post-commit booking confirmation delivery with customer-safe email content and a one-page result flow that preserves data after a contested slot.**

## Accomplishments

- Inserts one confirmation outbox record with the committed appointment and sends only after commit.
- Marks mail delivery sent or delayed without rolling back the scheduled booking.
- Displays appointment confirmation and recovery guidance; conflict refreshes slots without clearing customer fields.

## Task Commits

1. Task 1 — `1d595da`
2. Task 2 — `9db96f0`
3. Browser smoke scaffold — `f517b35`

## Deviations from Plan

### Auto-fixed Issues

1. [Rule 1 - Bug] Replaced incompatible Reflex application script configuration with page-level `rx.script` and documented `rx.call_script` callback usage.

## Issues Encountered

The Playwright test is intentionally guarded and was skipped because this host cannot reach the Compose browser ports. It is not counted as verified.

## Self-Check: PASSED

- Notification dispatcher, public state, browser smoke file, and task commits exist.
