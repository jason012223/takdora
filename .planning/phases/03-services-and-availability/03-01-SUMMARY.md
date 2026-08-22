---
phase: 03-services-and-availability
plan: 01
subsystem: service-catalog
tags: [reflex, sqlmodel, tenancy, decimal]
requires:
  - phase: 02-owner-workspaces-and-business-setup
    provides: authenticated owner and owner-derived business workspace
provides:
  - tenant-safe fixed-duration service catalog
  - customer-safe price projection and active-service readiness adapter
affects: [public-booking, owner-booking-operations, invoices]
actuals:
  tokens: 11125
  tasks: 2
  commits: 1
tech-stack:
  added: []
  patterns: [owner-derived catalog commands, non-destructive service lifecycle]
key-files:
  created: [takdora/services.py, takdora/pages/services.py, tests/test_services.py]
  modified: [takdora/models.py, takdora/business_setup.py]
key-decisions:
  - "Service prices remain nullable and always display as Price on request when absent."
  - "Services are deactivated rather than deleted so later booking and invoice references remain valid."
requirements-completed: [SERV-01]
coverage:
  - id: D1
    description: Tenant-safe fixed-duration catalog validation and customer price projection.
    requirement: SERV-01
    verification:
      - kind: unit
        ref: tests/test_services.py
        status: pass
    human_judgment: false
status: complete
---

# Phase 03 Plan 01: Service Catalog Summary

**Tenant-scoped fixed-duration services with safe optional PHP pricing and non-destructive activation state.**

## Accomplishments

- Added `BusinessService` persistence and server-side validation for names, fixed duration, description, and Decimal prices.
- Added private owner catalog UI and publication readiness adapter that reads live active-service state.
- Ensured inactive services cannot enter a customer-facing projection.

## Task Commits

1. **Tasks 1–2: service catalog and lifecycle** — `9f13579`

## Verification

- `uv run pytest tests/test_services.py tests/test_business_setup.py -q` — 16 passed
- `uv run ruff format --check takdora tests` — passed
- `uv run ruff check takdora tests` — passed

## Deviations from Plan

None - plan executed as a single cohesive catalog commit.

## Self-Check: PASSED
