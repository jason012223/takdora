# Phase 2: Owner Workspaces and Business Setup - Context

**Gathered:** 2026-08-22
**Status:** Ready for planning

<domain>
## Phase Boundary

Let a verified business owner create one isolated business workspace and configure the information needed to publish a clear public booking page. This phase covers owner authentication, onboarding, tenant isolation, and business setup; it does not add services, availability, or bookings.

</domain>

<decisions>
## Implementation Decisions

### Minimal Owner Onboarding
- **D-01:** Use a short guided setup wizard followed by the dashboard; minimize steps and fields for a better owner experience.
- **D-02:** Require only business name, public URL, one service, and working hours before the booking page can publish.
- **D-03:** Let owners start setup immediately, but require email verification before they publish.
- **D-04:** Use `takdora.app/b/{business-name}` as the public URL; generate it from the business name and let the owner edit it before publishing. — **Reversibility:** costly — changing public URL structure affects published links, routing, and future redirects.
- **D-05:** After setup, show a completion screen with optional next steps rather than dropping owners into a complex dashboard.
- **D-06:** Apply a polished Takdora default appearance when the owner skips logo and color configuration.
- **D-07:** Save wizard progress automatically and allow owners to resume unfinished setup.
- **D-08:** Show a final review screen with the public URL and missing optional details before publishing.

### Ownership and Public Address Behavior
- **D-09:** Support one business workspace per owner account in v1.
- **D-10:** Deleting a business requires deliberate confirmation, immediately deactivates its public page, and schedules data deletion.
- **D-11:** Allow only the creating owner to access the business dashboard in v1; preserve a model that can support team access later.
- **D-12:** Allow a published public URL to change and redirect the prior URL to the new one. — **Reversibility:** costly — public redirects become part of the customer-facing URL contract.

### the agent's Discretion
- Choose the wizard step count, exact default visual style, password/session mechanics, and data-deletion retention timing within the decisions above.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project scope
- `.planning/PROJECT.md` — configurable Philippines-first business model and security constraints.
- `.planning/REQUIREMENTS.md` — Phase 2 requirements AUTH-01 through AUTH-03, TEN-01 through TEN-02, and BIZ-01 through BIZ-04.
- `.planning/ROADMAP.md` — Phase 2 goal and observable success criteria.

### Prior phase decisions
- `.planning/phases/01-deployable-foundation/01-CONTEXT.md` — Docker/Render/CI and deployment-quality decisions Phase 2 must inherit.

### Research
- `.planning/research/ARCHITECTURE.md` — tenant isolation and membership-boundary guidance.
- `.planning/research/FEATURES.md` — owner dashboard and guided setup expectations.
- `.planning/research/SUMMARY.md` — shared-schema tenant model and product defaults.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- None yet — the project is greenfield pending Phase 1 implementation.

### Established Patterns
- Docker Compose locally, Render deployment, and required CI quality checks are locked by Phase 1.

### Integration Points
- Authentication and business setup will connect to the Django foundation created in Phase 1.
- Public routes must use the path-based business URL contract and preserve redirects after a slug change.

</code_context>

<specifics>
## Specific Ideas

- Favor as few owner actions and fields as possible without making publishing unsafe or incomplete.
- Default branding should look polished even before a business customizes it.

</specifics>

<deferred>
## Deferred Ideas

- Invited teammates and staff dashboard access — future phase after v1.

</deferred>

---

*Phase: 2-Owner Workspaces and Business Setup*
*Context gathered: 2026-08-22*
