# Phase 1: Deployable Foundation - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-08-22
**Phase:** 1-Deployable Foundation
**Areas discussed:** Hosting and Deployment, Testing and Release Checks

---

## Hosting and Deployment

| Option | Description | Selected |
|--------|-------------|----------|
| Render | Managed Django/PostgreSQL deployment | ✓ |
| Railway | Convenient developer experience with different runtime tradeoffs | |
| Fly.io | More infrastructure control with more setup | |

**User's choice:** Render.
**Notes:** Local development will use Docker Compose; merges to `main` auto-deploy; health checks and Sentry are required.

---

## Testing and Release Checks

| Option | Description | Selected |
|--------|-------------|----------|
| Required CI checks | Formatting, linting, and tests block merges | ✓ |
| Tests only | Only automated tests block merges | |
| Local-only checks | No merge block initially | |

**User's choice:** Required CI checks.
**Notes:** Prioritize security/business rules, include Playwright smoke tests, report coverage without a threshold, and run dependency vulnerability scanning.

---

## the agent's Discretion

- Exact framework tooling and configuration details within the locked decisions.

## Deferred Ideas

None.
