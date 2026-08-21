# Phase 1: Deployable Foundation - Context

**Gathered:** 2026-08-22
**Status:** Ready for planning

<domain>
## Phase Boundary

Create the secure, testable, deployable Django/PostgreSQL foundation for Takdora. This phase establishes the local developer workflow, continuous checks, production deployment, and operational visibility; it does not yet implement business accounts, booking, or invoices.

</domain>

<decisions>
## Implementation Decisions

### Hosting and Deployment
- **D-01:** Deploy the first public Takdora environment on Render. — **Reversibility:** costly — moving later changes hosting configuration, managed PostgreSQL connections, deployment integration, and operational runbooks.
- **D-02:** Use Docker Compose for local development so Django and PostgreSQL start together with a consistent command.
- **D-03:** Automatically deploy approved code merged into `main` to the Render production environment. — **Reversibility:** costly — changing the release policy affects repository protection, deployment hooks, and operational expectations.
- **D-04:** Provide both a health-check endpoint and Sentry error tracking from the first release.

### Testing and Release Checks
- **D-05:** Block merges to `main` unless formatting, linting, and automated tests pass. — **Reversibility:** costly — this becomes a repository quality and release-protection policy.
- **D-06:** Focus early automated tests on security and core business rules, and include Playwright browser smoke tests.
- **D-07:** Report code coverage in CI without enforcing a percentage threshold initially.
- **D-08:** Run a lightweight dependency vulnerability scan in CI.

### the agent's Discretion
- Select the exact Django project layout, Python package tooling, lint/format tools, GitHub Actions implementation, and Sentry/Render configuration consistent with the decisions above.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project scope
- `.planning/PROJECT.md` — product constraints, core value, and deployment requirement.
- `.planning/REQUIREMENTS.md` — Phase 1 requirements FOUND-02 and FOUND-03.
- `.planning/ROADMAP.md` — Phase 1 goal, dependency position, and success criteria.

### Research
- `.planning/research/STACK.md` — recommended Django/PostgreSQL, Docker, Render, CI, and monitoring stack.
- `.planning/research/SUMMARY.md` — product-wide architecture, deployment, and risk guidance.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- None — Takdora is a greenfield repository.

### Established Patterns
- None — Phase 1 establishes the initial project conventions.

### Integration Points
- Render will deploy from the repository's `main` branch.
- Docker Compose is the required local entry point for Django and PostgreSQL.

</code_context>

<specifics>
## Specific Ideas

- The project must be a real publicly deployable portfolio application, not only a local demo.
- Playwright should cover browser-level smoke tests alongside lower-level security and business-rule tests.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 1-Deployable Foundation*
*Context gathered: 2026-08-22*
