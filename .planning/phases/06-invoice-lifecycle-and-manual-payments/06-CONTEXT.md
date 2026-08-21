# Phase 6: Invoice Lifecycle and Manual Payments - Context

**Gathered:** 2026-08-22
**Status:** Ready for planning

<domain>
## Phase Boundary

Let an owner turn a completed booking into a trustworthy, immutable invoice PDF, send it to the customer, and manually track payment state. This phase is BIR-aware but is not a registered BIR-compliance, electronic-invoicing, or tax-reporting system.

</domain>

<decisions>
## Implementation Decisions

### Drafting and Issuance
- **D-01:** An owner can start an invoice only after marking its booking completed.
- **D-02:** Start the draft pre-filled from the booking, while allowing the owner to edit customer details, line items, dates, and notes before issue.
- **D-03:** Assign a simple automatic sequential number per business, such as `INV-0001`; do not offer prefixes or manual numbering in v1.
- **D-04:** Generate and freeze the PDF immediately when the owner issues an invoice.
- **D-05:** An issued invoice is immutable. To correct it, void it and create a new draft rather than editing or replacing the issued document. â€” **Reversibility:** costly - issued invoice snapshots and numbers become a historical record.

### Payment Tracking and Communication
- **D-06:** Support outstanding, partially paid, paid, and void statuses with plain-language labels.
- **D-07:** For partial payment, owners enter one total amount received. Takdora calculates the remaining balance; it does not record individual payments in v1.
- **D-08:** Owners can email an issued PDF directly to the customer from Takdora.
- **D-09:** Payment-status changes are internal by default, with an optional customer email.

### Presentation and Regulatory Boundary
- **D-10:** Use one professional Takdora invoice template that applies the business's logo, colors, and stored invoice details.
- **D-11:** Provide BIR-aware configurable fields and tax-line support, but clearly state that Takdora is not a BIR-registered/compliant electronic invoicing or sales-reporting system. Do not make a BIR-compliance claim.

### the agent's Discretion
- Choose supported tax-line fields, payment-email wording, PDF storage naming, exact void/draft flow, invoice-number padding, and validation/error messages within the non-compliance boundary.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project scope
- `.planning/PROJECT.md` - v1 manual payment scope and Philippines-first product boundary.
- `.planning/REQUIREMENTS.md` - Phase 6 requirements INV-01 through INV-08.
- `.planning/ROADMAP.md` - Phase 6 goal and observable success criteria.

### Prior phase decisions
- `.planning/phases/02-owner-workspaces-and-business-setup/02-CONTEXT.md` - business invoice identity fields and tenant boundary.
- `.planning/phases/04-safe-public-booking/04-CONTEXT.md` - customer details and established email behavior.
- `.planning/phases/05-owner-booking-operations/05-CONTEXT.md` - completed booking prerequisite.
- `.planning/phases/01-deployable-foundation/01-CONTEXT.md` - production configuration and quality gates.

### Research and external authority
- `.planning/research/ARCHITECTURE.md` - immutable invoice snapshots, Decimal money, and private document access.
- `.planning/research/PITFALLS.md` - money, PDF, and document-security risks.
- [BIR Revenue Regulations No. 11-2025](https://bir-cdn.bir.gov.ph/BIR/pdf/RR%20No.%2011-2025.pdf) - electronic-invoice and sales-reporting scope.
- [BIR Revenue Regulations No. 7-2024](https://bir-cdn.bir.gov.ph/BIR/pdf/RR%207-2024%20%28final%29.pdf) - invoice requirements and taxpayer registration context.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- None yet - the project is greenfield pending preceding implementation phases.

### Established Patterns
- A booking becomes completed only through an explicit owner action.
- Business identity and branding are configurable per isolated workspace.
- Customer email delivery begins only after successful committed business actions.

### Integration Points
- Invoice totals require exact decimal money handling and must snapshot business, customer, service, and line-item data at issue time.
- Private PDFs require persistent object storage and tenant-scoped authorization, completed in Phase 7 hardening.
- Issued-invoice email and optional payment-update emails use the established transactional email path.

</code_context>

<specifics>
## Specific Ideas

- Keep manual payment tracking concise: one received-total field rather than a payments ledger.
- A polished single template should look professional by default while accurately carrying configured business details.

</specifics>

<deferred>
## Deferred Ideas

- BIR registration, structured e-invoice generation, electronic sales reporting, and any BIR-compliance claim.
- Online payment providers and reconciliation.
- Individual payment records, methods, and dates.

</deferred>

---

*Phase: 6-Invoice Lifecycle and Manual Payments*
*Context gathered: 2026-08-22*
