# Domain Pitfalls

**Domain:** Configurable multi-tenant service booking and invoice application
**Researched:** 2026-08-22
**Overall confidence:** MEDIUM — findings are cross-checked against current primary Django/PostgreSQL/BIR documents and OWASP guidance.

## Critical Pitfalls

### Pitfall 1: Tenant data leaks through object IDs or unscoped queries

**Confidence:** MEDIUM

**What goes wrong:** A logged-in owner changes an invoice, booking, service, PDF URL, or settings ID in a URL/request and reads or mutates another business's data.

**Why it happens:** Tenant filtering is applied in views sometimes, but not consistently in query helpers, exports, background email jobs, or file download endpoints. Login alone is mistaken for authorization.

**Consequences:** Exposure of customer names, contact details, schedules, invoices, and business information; corrupted records; an unacceptable public-launch security failure.

**Prevention:** Put `business_id` on every tenant-owned model; resolve the active business from the authenticated membership, never from a client-supplied ID; make every repository/query helper tenant-scoped; authorize the object and its state for every mutating action. Use database row-level security only as later defense in depth, not as the first implementation dependency.

**Detection:** Authorization regression tests with two businesses for every detail, update, delete, PDF-download, and dashboard route; log denied cross-tenant attempts; add code review checks for unscoped `.get(pk=...)` calls.

### Pitfall 2: Double bookings caused by a check-then-insert race

**Confidence:** MEDIUM

**What goes wrong:** Two customers see one apparently free slot and both bookings succeed, especially during busy periods or a retry after a slow request.

**Why it happens:** Availability is calculated before insertion and application code assumes that result remains true. A `UNIQUE(start_time)` constraint cannot protect variable-duration or overlapping appointments.

**Consequences:** The business must manually apologize, reschedule, or cancel; the core promise of Takdora becomes untrustworthy.

**Prevention:** Store every appointment as timezone-aware start/end instants. In a short database transaction, re-evaluate availability and create the booking. On PostgreSQL, enforce no overlap per bookable resource with a range/exclusion constraint (or an equivalent database-enforced slot rule), then translate its integrity error into “that time was just taken.” Do not deploy SQLite as the production concurrency guarantee.

**Detection:** Concurrent integration tests submitting the same slot; production metric for constraint conflicts; tests for edge boundaries (one appointment ending exactly when the next starts), service-duration changes, owner-created bookings, and reschedules.

### Pitfall 3: Incorrect or mutable invoice records

**Confidence:** MEDIUM

**What goes wrong:** A later service-price, currency, tax, business-profile, or customer-name edit changes an already-issued invoice or a regenerated PDF differs from the original.

**Why it happens:** The invoice simply reads live `Service` and `Business` fields rather than an issue-time snapshot; money is stored/calculated using binary floating point; invoice numbers are assigned outside a safe transaction.

**Consequences:** Incorrect totals, duplicate/gapped identifiers, unreconcilable PDFs, and possible accounting/compliance problems.

**Prevention:** Treat an issued invoice as an immutable ledger record: snapshot seller/customer details, line description, quantity, unit price, tax/rate, currency, total, issue date, and sequential number at issuance. Use decimal minor-unit/`Decimal` arithmetic with explicit currency rounding. Version or store the exact generated PDF. Allow corrections only through void/credit-and-reissue workflow, even if v1 keeps it simple.

**Detection:** Golden-PDF and total-calculation tests; test that changing a service does not change issued invoices; unique constraint and concurrent test for per-business invoice numbers; audit trail for issue/void/paid transitions.

### Pitfall 4: Treating a generated PDF as automatically BIR-compliant e-invoicing

**Confidence:** MEDIUM

**What goes wrong:** Takdora markets every PDF as a legally compliant Philippine electronic invoice, even though the business may need registered/accredited tooling and structured invoice data/reporting.

**Why it happens:** “PDF invoice” is conflated with the BIR definition of an electronic invoice.

**Consequences:** Misleading product claims and avoidable customer tax/compliance risk.

**Prevention:** Scope v1 as configurable invoice-document generation and manual payment tracking, not tax filing/compliance. Require an owner-provided invoice prefix/registration details where applicable; state that the business is responsible for BIR compliance; obtain Philippine accounting/legal review before compliance claims or BIR electronic-sales-reporting features.

**Detection:** Product copy and PDF-template review against current BIR regulations at release; block terms such as “BIR-compliant” until counsel/registration evidence is recorded.

## Moderate Pitfalls

### Pitfall 1: Time zone, opening-hour, and booking-rule ambiguity

**What goes wrong:** A noon booking shifts, an appointment is offered during a closed break, or a daylight-saving-capable future tenant gets invalid time calculations.

**Prevention:** Store instants in UTC; store each business IANA timezone (default `Asia/Manila`); calculate availability from explicit weekly intervals, breaks, lead time, booking horizon, duration, and resource capacity; show timezone in owner and confirmation screens. Freeze the booked start/end and service snapshot.

### Pitfall 2: Email confirmation is treated as part of the booking transaction

**What goes wrong:** SMTP downtime makes a valid booking appear failed, or retries send multiple confirmations.

**Prevention:** Commit booking first; enqueue a durable, idempotent notification after commit; expose owner-visible delivery status and retry. Never log full email provider credentials or confirmation contents.

### Pitfall 3: Public booking abuse and privacy exposure

**What goes wrong:** Bots fill calendars, booking endpoints are spammed, or customer data appears in URLs, logs, analytics, and exception reports.

**Prevention:** Rate-limit by business/IP, validate server-side, add a progressive bot challenge only when abuse appears, minimize required customer fields, encrypt secrets, use HTTPS, and use opaque file/object identifiers rather than predictable paths.

### Pitfall 4: Deployment defaults quietly fail in production

**What goes wrong:** Static assets/PDF fonts are missing, email is not configured, migrations are skipped, `DEBUG` or weak secrets remain enabled, host/CSRF configuration rejects public traffic, or ephemeral storage loses uploaded branding/PDFs.

**Prevention:** Twelve-factor environment configuration, production startup/migration checklist, managed PostgreSQL, object storage for uploads/artifacts, health check, error monitoring, backups and restore test. Run Django’s deployment checks in CI and deploy a staging smoke test.

## Minor Pitfalls

### Pitfall 1: No auditability for owner actions

**What goes wrong:** An owner cannot tell who rescheduled, cancelled, issued, or marked an invoice paid.

**Prevention:** Append actor/time/action records for lifecycle changes and retain prior booking times/statuses.

### Pitfall 2: Configuration creates impossible schedules

**What goes wrong:** An owner sets a negative buffer, an overlapping opening interval, a service with no duration, or removes a service with future bookings.

**Prevention:** Validate configuration at write time; use safe defaults; retain/inactivate referenced services instead of destructive deletion.

## Phase-Specific Warnings

| Phase topic | Likely pitfall | Mitigation |
|-------------|----------------|------------|
| Foundation, accounts, tenant model | IDOR / missing tenant scope | Model membership explicitly; tenant-scoped data access; two-tenant authorization test fixture from day one. |
| Business configuration and availability | Ambiguous hours/timezones and impossible rules | UTC instants + IANA business timezone; explicit rule validation and boundary tests. |
| Public booking | Race conditions and bot abuse | Database-enforced overlap invariant; atomic create; concurrent request tests; rate limiting. |
| Owner booking management | Reschedule creates overlap or destroys history | Reuse the same overlap invariant; audit state transitions; do not hard-delete referenced data. |
| Email confirmations | Failed/double sends | After-commit idempotent job with retry and delivery observability. |
| Invoice PDFs/manual payment | Live-data mutation, rounding, legal overclaim | Immutable snapshots/Decimal/unique numbering; review labels and claims against BIR guidance. |
| Deployment and release | Secrets/static/PDF/storage/migrations failure | Production checklist, managed services, CI deployment check, staging end-to-end smoke test and restore drill. |

## Sources

- [OWASP Multi-tenant Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Multi_Tenant_Security_Cheat_Sheet.html) — MEDIUM (current authoritative security guidance)
- [OWASP Authorization Regression Testing Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Regression_Testing_Cheat_Sheet.html) — MEDIUM
- [Django QuerySet `select_for_update()` documentation](https://docs.djangoproject.com/en/stable/ref/models/querysets/#select-for-update) — MEDIUM
- [PostgreSQL exclusion constraints](https://www.postgresql.org/docs/current/ddl-constraints.html#DDL-CONSTRAINTS-EXCLUSION) — MEDIUM
- [BIR Revenue Regulation No. 11-2025](https://bir-cdn.bir.gov.ph/BIR/pdf/RR%20No.%2011-2025.pdf) — MEDIUM; compliance interpretation needs professional review
- [BIR Revenue Regulation No. 7-2024](https://bir-cdn.bir.gov.ph/BIR/pdf/RR%207-2024%20%28final%29.pdf) — MEDIUM; compliance interpretation needs professional review
