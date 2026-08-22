---
phase: 04-safe-public-booking
plan: 01
subsystem: public-booking
tags: [reflex, public-routing, timezone, availability]
requires:
  - phase: 03-services-and-availability
    provides: authoritative UTC availability slots
provides:
  - published-only public business resolver and canonical redirect behavior
  - focused anonymous booking page with browser-local slot display
affects: [04-02, 04-03, owner-booking-operations]
actuals:
  tokens: 6500
  tasks: 2
  commits: 2
tech-stack:
  added: []
  patterns: [public projection boundary, browser timezone as display preference]
key-files:
  created: [takdora/public_booking.py, takdora/pages/public_booking.py]
  modified: [takdora/models.py, takdora/business_setup.py, takdora/takdora.py]
key-decisions:
  - "Public resolver exposes only active services from an active published non-deleting workspace."
  - "UTC remains the slot identity while browser IANA timezone changes presentation only."
requirements-completed: [BOOK-01, BOOK-02, BOOK-03]
coverage:
  - id: D1
    description: Public timezone validation and focused booking form composition
    requirement: BOOK-01
    verification:
      - kind: unit
        ref: tests/test_public_booking.py and tests/test_public_booking_page.py
        status: pass
    human_judgment: false
duration: 38min
completed: 2026-08-22
status: complete
---

# Phase 04 Plan 01: Safe public address and compact booking page Summary

**Published-business resolver and single-screen anonymous booking form that projects authoritative UTC availability into a visitor-local display.**

## Accomplishments

- Added a server-authorized publish command and an anonymous public projection that excludes private workspace data.
- Added canonical `/b/{slug}` routing, retained-slug redirect handling, a privacy page, and direct phone/note fields.
- Validated browser timezone identifiers and use them only for formatting slots from the Phase 3 engine.

## Task Commits

1. Task 1 — `2394084`
2. Task 2 — `400b77d`

## Deviations from Plan

None - plan executed with existing Reflex and Python standard-library dependencies.

## Self-Check: PASSED

- Public resolver/page files and both task commits exist.
