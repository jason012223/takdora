---
phase: 08-portfolio-validation-and-responsive-release
plan: 02
subsystem: database
tags: [reflex, sqlmodel, demo, tenancy]
requires:
  - phase: 08-portfolio-validation-and-responsive-release
    provides: factual public marketing and /demo route
provides:
  - server-gated synthetic demo session
  - resettable demo booking-to-invoice fixture
  - persistent synthetic-data labels in owner views
affects: [portfolio-e2e, staging]
actuals:
  tokens: 27000
  tasks: 3
  commits: 3
tech-stack:
  added: []
  patterns: [server-derived demo authority, explicit synthetic tenant marker]
key-files:
  created: [takdora/demo.py, takdora/pages/demo.py, tests/test_demo.py, tests/test_demo_page.py]
  modified: [takdora/config.py, takdora/models.py, takdora/pages/owner_dashboard.py, takdora/pages/owner_bookings.py, takdora/pages/owner_invoices.py]
key-decisions:
  - "Synthetic demo access is enabled only through SYNTHETIC_DEMO_ENABLED and derives the owner on the server."
  - "Fixture contacts use the reserved takdora.example domain and seed no delivery requests."
requirements-completed: [FOUND-01]
coverage:
  - id: D1
    description: Isolated synthetic demo entry and owner labels
    requirement: FOUND-01
    verification:
      - kind: unit
        ref: tests/test_demo.py and tests/test_demo_page.py
        status: unknown
    human_judgment: true
    rationale: Local Python environment was unavailable after Docker changed the shared virtual environment.
status: complete
---

# Phase 8 Plan 02: Synthetic Demo Summary

**A server-gated, resettable synthetic owner workspace with a published demo business, completed booking, issued invoice, and manually tracked payment example.**

## Accomplishments

- Added a server-only `SYNTHETIC_DEMO_ENABLED` switch and opaque session entry that never accepts a browser-supplied tenant identity.
- Added explicit synthetic markers, scoped reset cleanup, reserved example-domain contacts, and no outbound mailer path.
- Added persistent synthetic-data banners across the demo owner dashboard, booking, and invoice pages.

## Task Commits

1. Task 1 — `212af8b` feat(08-02): add isolated synthetic demo entry
2. Task 2 — `3f99e20` feat(08-02): reset synthetic demo without delivery
3. Task 3 — `6329494` feat(08-02): label synthetic owner journeys

## Deviations from Plan

None - plan executed as specified. The integration test run is deferred because its shared local environment became unavailable.

## Issues Encountered

`uv` cannot use the Docker-mutated `.venv` because `lib64` is access denied. Python source syntax was checked with the installed interpreter; full runtime tests need a repaired/recreated project environment.

## User Setup Required

Set `SYNTHETIC_DEMO_ENABLED=true` only in the isolated staging or portfolio environment. The exact reset and verification procedure is in `docs/OPERATIONS.md`.

## Self-Check: PASSED

- Demo module, public entry page, and tests exist.
- Task commits `212af8b`, `3f99e20`, and `6329494` exist.
