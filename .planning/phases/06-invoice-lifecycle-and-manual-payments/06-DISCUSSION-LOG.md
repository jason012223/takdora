# Phase 6: Invoice Lifecycle and Manual Payments - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md - this log preserves the alternatives considered.

**Date:** 2026-08-22
**Phase:** 6-Invoice Lifecycle and Manual Payments
**Areas discussed:** Invoice timing, drafting, numbering, payments, correction, PDFs, BIR boundary, delivery, template

---

## Invoice Start

| Option | Description | Selected |
|--------|-------------|----------|
| Completed booking only | Start only after owner marks the booking completed | x |
| Scheduled booking | Allow a draft earlier | |
| Automatic on booking | Create an invoice on customer submission | |

**User's choice:** Completed booking only.

---

## Draft and Numbering

| Option | Description | Selected |
|--------|-------------|----------|
| Editable pre-filled draft | Use booking data and let owner edit it | x |
| Locked pre-filled draft | Do not permit booking details to change | |
| Blank draft | Enter every field manually | |

**User's choice:** Editable pre-filled draft.
**Notes:** Use an automatic simple sequence per business, such as `INV-0001`.

---

## Payment State

| Option | Description | Selected |
|--------|-------------|----------|
| Outstanding and paid | Two-state manual tracking | |
| Outstanding, paid, void | Add void | |
| Outstanding, partially paid, paid, void | Support a remaining balance | x |

**User's choice:** Outstanding, partially paid, paid, void.
**Notes:** Owner enters one amount-received total; do not add individual payment records.

---

## Correction and PDF

| Option | Description | Selected |
|--------|-------------|----------|
| Void and new draft | Issued invoice is immutable | x |
| Edit with history | Change issued data with an audit log | |
| Replace PDF | Edit and overwrite without history | |

**User's choice:** Void and new draft.
**Notes:** Generate and freeze the PDF at issue time.

---

## Philippine Invoice Boundary

| Option | Description | Selected |
|--------|-------------|----------|
| BIR-aware template | Configurable fields without a compliance claim | x |
| Full BIR compliance | Registration, structured invoices, reporting, legal review | |
| Simple line items | No tax-related fields | |

**User's choice:** BIR-aware template.
**Notes:** User originally selected full BIR format; after official BIR research established the much broader compliance scope, chose the safe non-compliance option.

---

## Delivery and Payment Email

| Option | Description | Selected |
|--------|-------------|----------|
| Owner sends PDF manually | Download and send outside Takdora | |
| Takdora emails PDF | Owner sends the issued PDF from the app | x |
| Customer link | Share a public/customer PDF URL | |

**User's choice:** Takdora emails PDF.
**Notes:** Payment-status email is optional; use one professional branded invoice template.

---

## the agent's Discretion

- Field details, email copy, numbering padding, and document storage conventions.

## Deferred Ideas

- BIR-compliant e-invoicing/sales reporting.
- Online payments and individual payment records.
