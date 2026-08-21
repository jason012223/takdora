# Phase 7: Reliability and Launch Hardening - Context

**Gathered:** 2026-08-22
**Status:** Ready for planning

<domain>
## Phase Boundary

Make the deployed service observable, recoverable, private, and ready for release. This phase hardens the established booking, email, PDF, storage, and deployment paths; it does not add new customer or invoice product features.

</domain>

<decisions>
## Implementation Decisions

### Failure Visibility and Customer Recovery
- **D-01:** Surface email/PDF-generation or delivery failures as a clear retryable owner-dashboard state and alert the operator through monitoring.
- **D-02:** When confirmation email delivery fails after a booking commits, keep the booking confirmed. Show the customer the appointment details, a clear email-delay explanation, business contact information, and next steps; retry delivery automatically. Never make a persisted booking appear failed solely because outbound email failed. â€” **Reversibility:** costly - this is a core customer trust and data-integrity contract.

### Release Experience
- **D-03:** During planned downtime, use a branded maintenance page with a plain-language message and business contact route rather than a technical error page.
- **D-04:** Verify the real booking-to-invoice workflow in a separate staging environment with test data before each production release.

### Required Technical Safeguards
- **D-05:** Retain Phase 1 safeguards: production health checks, error monitoring, automatic deploy after CI, dependency scans, and business/security regression tests.
- **D-06:** Keep issued PDFs private and persist logos/PDFs outside ephemeral application storage; enforce tenant-scoped authorization for all private records and documents.
- **D-07:** Maintain repeatable backup, migration, release-check, and recovery procedures as technical acceptance criteria.

### the agent's Discretion
- Choose monitoring alert thresholds/channels, retry schedule and cap, staging-provider topology, maintenance-page copy, backup retention, signed-document access design, and release-check implementation.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project scope
- `.planning/PROJECT.md` - deployable-product and private-data constraints.
- `.planning/REQUIREMENTS.md` - Phase 7 requirements REL-01 through REL-04.
- `.planning/ROADMAP.md` - Phase 7 goal and observable success criteria.

### Prior phase decisions
- `.planning/phases/01-deployable-foundation/01-CONTEXT.md` - Docker, deployment, CI, health check, Sentry, coverage, and vulnerability-scan decisions.
- `.planning/phases/04-safe-public-booking/04-CONTEXT.md` - customer confirmation and contact expectations.
- `.planning/phases/06-invoice-lifecycle-and-manual-payments/06-CONTEXT.md` - issued PDFs, private invoices, email delivery, and immutable documents.

### Research
- `.planning/research/STACK.md` - infrastructure candidates, with the Reflex supersession note.
- `.planning/research/ARCHITECTURE.md` - storage, tenant isolation, and delivery sequencing.
- `.planning/research/PITFALLS.md` - error handling, document privacy, and deployment risks.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- None yet - the project is greenfield pending preceding implementation phases.

### Established Patterns
- CI quality gates and monitoring are part of the initial deployable foundation.
- Bookings are committed before confirmation email, invoices are immutable at issue, and private data is tenant-scoped.

### Integration Points
- Delivery jobs need idempotent retry behavior so retries never duplicate emails or documents.
- Staging must exercise public booking, owner completion, issue, email, and private-PDF access with isolated test data.
- Maintenance and health routes must operate with the Reflex deployment convention finalized by Phase 01.1.

</code_context>

<specifics>
## Specific Ideas

- Failure language should tell customers exactly what succeeded, what was delayed, and what to do next.
- Keep operational complexity hidden from owners unless they have a direct recovery action.

</specifics>

<deferred>
## Deferred Ideas

- Advanced incident-management integrations and customer-facing service-status history.

</deferred>

---

*Phase: 7-Reliability and Launch Hardening*
*Context gathered: 2026-08-22*
