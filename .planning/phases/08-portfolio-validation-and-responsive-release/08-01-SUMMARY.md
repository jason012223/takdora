---
phase: 08-portfolio-validation-and-responsive-release
plan: 01
subsystem: ui
tags: [reflex, radix, marketing, accessibility]
requires:
  - phase: 07-reliability-and-launch-hardening
    provides: deployable Reflex application and release safeguards
provides:
  - factual multi-page marketing routes
  - direct registration and labelled demo paths
affects: [portfolio-demo, responsive-browser-tests]
actuals:
  tokens: 13300
  tasks: 3
  commits: 3
tech-stack:
  added: []
  patterns: [shared marketing layout, central reviewed content boundary]
key-files:
  created: [takdora/pages/marketing.py, tests/test_marketing_pages.py, tests/test_marketing_content.py]
  modified: [takdora/ui/layouts.py, takdora/takdora.py]
key-decisions:
  - "Marketing routes use direct /register links and label /demo as synthetic supporting exploration."
  - "V1 payment and BIR boundaries are reviewed constants with regression tests."
requirements-completed: [FOUND-01]
coverage:
  - id: D1
    description: Factual marketing route composition and direct registration/demo links
    requirement: FOUND-01
    verification:
      - kind: unit
        ref: tests/test_marketing_pages.py
        status: pass
    human_judgment: true
    rationale: Visual hierarchy and responsive presentation require browser review.
  - id: D2
    description: Synthetic-demo, manual-payment, and invoice-claim boundaries
    requirement: FOUND-01
    verification:
      - kind: unit
        ref: tests/test_marketing_content.py
        status: pass
    human_judgment: false
status: complete
---

# Phase 8 Plan 01: Marketing Surface Summary

**Factual Reflex marketing pages that guide real owners to registration while clearly separating the synthetic reviewer demo.**

## Accomplishments

- Replaced the readiness landing route with an accessible Takdora home page and a primary `/register` action.
- Added shared navigation plus focused features, help, and portfolio routes.
- Added narrow regression tests for prohibited evidence claims and the manual-payment/BIR boundary.

## Task Commits

1. Task 1 — `c6659a5` feat(08-01): route factual home page to registration
2. Task 2 — `bf6e9cc` feat(08-01): add factual marketing information pages
3. Task 3 — `efa5137` test(08-01): guard factual marketing copy

## Deviations from Plan

### Auto-fixed Issues

1. [Rule 1 - Bug] Kept every navigation target visible at mobile widths rather than showing an inert menu button.
- Found during: subsequent responsive tracer work.
- Fix: replaced the hidden mobile links/menu affordance with wrapping links.
- Committed in: `a9cf5de`.

## Issues Encountered

The shared Windows `.venv` became an inaccessible Docker-created link after container execution. Focused marketing tests passed before that state change; the required `uv` full-suite verification remains blocked until the environment is repaired without deleting unknown local state.

## Self-Check: PASSED

- Created marketing module and tests exist in the repository.
- Task commits `c6659a5`, `bf6e9cc`, and `efa5137` exist.
