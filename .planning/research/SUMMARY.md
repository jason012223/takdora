# Project Research Summary

**Project:** Takdora  
**Domain:** Configurable multi-tenant booking and invoice web application for Philippine service businesses  
**Researched:** 2026-08-22  
**Confidence:** MEDIUM

## Executive Summary

Takdora should launch as a focused, server-rendered Django monolith for appointment-based businesses—not as a general business suite. An owner configures a branded public booking page, services, availability, booking rules, and invoice identity; a customer books an actually available time without creating an account; the owner then manages the booking and issues a PDF invoice with a manual payment state. The product's strongest differentiator is the reliable handoff from booking to invoice, with Philippines-friendly defaults (PHP and `Asia/Manila`) that remain configurable.

The recommended implementation is Python 3.13, Django 6.1, PostgreSQL, Django templates, HTMX, and customized Bootstrap. Use a shared-schema multi-tenant model with strict business scoping, Docker, managed PostgreSQL, object storage for logos/PDFs, Resend for email, and a paid always-on deployment. Start synchronous post-commit confirmation delivery only if necessary to keep the first flow small, but make the notification boundary durable from the outset; invoices and reliable retries justify a Celery/Redis worker once introduced.

The launch risks are correctness and trust, not UI novelty: cross-tenant data exposure, double bookings under concurrency, mutable or incorrectly rounded invoices, unreliable notifications, and unsupported BIR-compliance claims. Address them with tenant-first authorization tests, PostgreSQL-enforced overlap constraints plus idempotency keys, immutable Decimal-based invoice snapshots, transactional outbox delivery, private PDF storage, and explicit wording that v1 generates configurable invoice documents rather than guaranteeing tax compliance.

## Key Findings

### Recommended Stack

Django is the decisive choice because Takdora is dominated by secure forms, account workflows, admin operations, scheduling rules, and document generation. A templates-plus-HTMX approach delivers responsive interaction without splitting authentication, validation, routing, and deployment across a separate SPA/API. PostgreSQL is mandatory in production because its transaction and exclusion-constraint support protects overlapping appointments.

**Core technologies:**

- **Python 3.13 + Django 6.1:** full-stack foundation with custom user model, ORM, auth, migrations, forms, time-zone support, and security controls.
- **PostgreSQL 17 + psycopg:** authoritative booking and invoice datastore; supports tenant-first indexes and the required non-overlap invariant.
- **Django templates + HTMX 2 + django-htmx + Bootstrap 5:** accessible, responsive public and owner interfaces with minimal client complexity.
- **WeasyPrint + S3-compatible storage (`django-storages`, `boto3`):** render and retain immutable PDFs and business logos outside ephemeral web storage.
- **Resend:** transactional booking email after a verified sending domain; use a Takdora sender/reply-to strategy until per-business domains are verified.
- **Docker, Render, managed Render Postgres, Gunicorn/Uvicorn, GitHub Actions, Sentry:** repeatable public deployment, CI, deployment checks, and production observability.
- **Celery + Redis:** defer until the durable outbox needs retryable email/PDF work; do not let queue operations delay the core first booking flow.
- **Ruff + pytest/pytest-django + django-ratelimit:** code quality, booking/authorization regression coverage, and public-endpoint abuse protection.

### Expected Features

The v1 must complete one usable loop: setup a business, accept a conflict-safe booking, confirm it by email, manage it privately, and issue/track a PDF invoice. Build configuration as a first-class workflow so Takdora works for salons, tutors, freelancers, repair providers, and other one-capacity service businesses without vertical-specific code.

**Must have (table stakes):**

- Owner account, private dashboard, business profile/branding, stable public slug, and tenant isolation.
- Service catalog with name, duration, price, and active/inactive state.
- Weekly hours, exceptions/breaks, IANA time zone, lead time, booking horizon, slot interval, and buffer validation.
- Public available-slot flow, small customer form, conflict-safe booking creation, confirmation screen, and email confirmation.
- Owner agenda/list/detail, search/status filters, owner-only cancellation/rescheduling, history/audit data, and customer update emails.
- Booking-linked invoice draft, immutable issued PDF, per-business identity/currency, and `draft`/`issued`/`paid`/`void` manual payment state.

**Should have (competitive):**

- Guided setup checklist that reaches a shareable public URL.
- Configurable but opinionated PHP, Asia/Manila, and 30-minute-grid defaults.
- Booking-to-invoice prefill and an unpaid/paid receivables view.
- Low-friction mobile-friendly booking with no customer account; invoice preview only if schedule permits.

**Defer (v2+):**

- Online payments, deposits, refunds, provider webhooks, and reconciliation.
- Customer self-service cancellation/rescheduling, reminders/SMS, external calendars, social booking, and native apps.
- Multi-staff/resource/location capacity, recurring/group appointments, waitlists, marketplace discovery, accounting/tax filing, CRM, payroll, and claims of BIR compliance.

### Architecture Approach

Use a modular Django monolith with `accounts`, `tenancy`, `catalog`, `scheduling`, `bookings`, `billing`, `notifications`, `dashboard`, and `public` boundaries. Views and templates stay thin; domain commands own booking, reschedule, cancellation, invoice issue, and payment transitions. Every tenant-owned model carries `business_id`, and every private object is retrieved through the authorized active business. Public routes resolve only published configuration by slug; customer data and PDFs remain private.

**Major components:**

1. **Accounts and tenancy:** custom user, `Business`, `Membership`, roles, public slug, branding, and the tenant-scoped access boundary.
2. **Catalog and scheduling:** services, default resource, hours, closures, booking rules, candidate-slot calculation, and database-safe booking/reschedule commands.
3. **Bookings and notifications:** contact snapshots, lifecycle audit events, idempotency records, durable outbox, confirmation/update delivery state.
4. **Billing:** invoice numbering, immutable line and party snapshots, Decimal totals, manual payment transitions, PDF rendering, and private download authorization.
5. **Public and dashboard UI:** responsive server-rendered flows that call domain services rather than duplicating business rules.

### Critical Pitfalls

1. **Tenant data leaks:** scope every model/query/download/task by the server-resolved active business, never a client-supplied business ID; run two-tenant authorization regression tests on every private route.
2. **Double bookings:** displayed availability is advisory. Recheck in a short atomic transaction and enforce a PostgreSQL GiST exclusion constraint over a half-open UTC time range per resource; test concurrent submissions.
3. **Mutable or inaccurate invoices:** issue from immutable business/customer/service snapshots, Decimal monetary values, safe per-business sequencing, versioned PDFs, and audited void/reissue rather than destructive edits.
4. **Email/PDF inside transactions:** persist booking/invoice changes first, create an outbox record, and deliver/render asynchronously with idempotent retries and owner-visible failure state.
5. **Compliance and production overclaims:** call PDFs configurable invoice documents, not automatically BIR-compliant e-invoices; validate tax fields with a Philippine professional and harden secrets, storage, migrations, static assets, backups, and production settings before launch.

## Implications for Roadmap

Based on the combined research, use the following eight phases.

### Phase 1: Product Foundation and Deployable Shell

**Rationale:** The custom user model, environment separation, Docker runtime, PostgreSQL, CI, and secure settings must exist before domain migrations or public data are created.

**Delivers:** Django project, Python/Django lockfile, custom user migration, PostgreSQL local/production configuration, Docker, static assets, baseline landing/dashboard shell, CI lint/test/deployment checks, error monitoring, and secure environment configuration.

**Addresses:** Public deployability and responsive web baseline.

**Avoids:** Late user-model migration, ephemeral-storage loss, debug/secrets/CSRF/host deployment failures.

### Phase 2: Tenancy, Ownership, and Business Onboarding

**Rationale:** Every later feature handles private business and customer data, so the active-business boundary must be reliable before adding records that can leak.

**Delivers:** `Business`, `Membership`, owner authorization, tenant-scoped query conventions, public slug, branding/profile, invoice identity/currency defaults, dashboard context, guided setup checklist, and two-tenant access tests.

**Addresses:** Owner accounts, private dashboard, branded public page identity, PHP/Asia-Manila defaults.

**Avoids:** IDOR and unscoped-query leaks; client-controlled tenant IDs.

### Phase 3: Service Configuration and Availability Engine

**Rationale:** Booking cannot be correct until the catalog, default capacity resource, time-zone model, hours, closures, and rules can produce explainable candidate slots.

**Delivers:** Services, active/inactive lifecycle, default bookable resource, weekly intervals/breaks/closures, lead time, horizon, slot interval/buffer configuration, availability service, owner preview, and boundary/DST validation tests.

**Addresses:** Configurable services, working hours, booking rules, and genuine available times.

**Avoids:** Impossible schedules, ambiguous time zones, and a later rewrite for staff/resources by retaining a resource abstraction internally.

### Phase 4: Conflict-Safe Public Booking and Confirmation

**Rationale:** This is the first complete customer-facing value loop and depends on tenancy and availability. Correctness must be enforced in PostgreSQL, not trusted to the browser.

**Delivers:** Published public booking page, accessible mobile form, candidate slot refresh, customer/contact snapshot, idempotency token, atomic booking command, active-range exclusion constraint, rate limits, success page, and post-commit confirmation/outbox delivery with a delivery record.

**Addresses:** Public booking, exactly-once appointment creation, email confirmation, low-friction no-account customer flow.

**Avoids:** Double booking, duplicate retries, booking spam, and confirmation for a rolled-back booking.

### Phase 5: Owner Booking Operations

**Rationale:** Owners need to act on bookings before invoices can reflect real lifecycle decisions; rescheduling must reuse the same safe scheduling command.

**Delivers:** Agenda/list/detail views, filters, owner cancellation/reschedule, immutable booking history/audit events, and customer update emails.

**Addresses:** Owner-controlled changes and booking visibility.

**Avoids:** Direct timestamp edits, reschedule conflicts, hard deletion, and missing accountability.

### Phase 6: Invoice Lifecycle, PDFs, and Manual Payment Tracking

**Rationale:** Billing depends on stable business, customer, service, and booking facts. It should be built after booking operations to guarantee correct source data and states.

**Delivers:** Invoice drafts prefilled from bookings, editable draft line items, atomic per-business invoice number issuance, immutable snapshots, Decimal totals, PDF generation/storage/private download, `draft`/`issued`/`paid`/`void` state transitions, payment details/audit records, and unpaid/paid view.

**Addresses:** Booking-to-invoice handoff, downloadable PDF, invoice identity/currency, and manual paid status.

**Avoids:** Mutable historical records, rounding errors, PDF leaks, duplicate invoice numbers, and BIR-compliance claims.

### Phase 7: Reliability, Observability, and Production Hardening

**Rationale:** A portfolio demo becomes a usable public app only when failure modes around email, PDFs, uploads, privacy, and recovery are observable and tested.

**Delivers:** Celery/Redis worker if the outbox needs retryable delivery/PDF jobs, idempotent retry/sweep flow, object-storage policies, verified email sender, production monitoring, health checks, security headers/rate limits, backup/restore rehearsal, privacy/consent copy, and end-to-end smoke tests.

**Addresses:** Dependable confirmations/PDFs, public deployment, and launch readiness.

**Avoids:** Silent email failures, missing fonts/files, PII exposure, unavailable public service, and unrecoverable data loss.

### Phase 8: Portfolio Polish and Usability Validation

**Rationale:** The core is now safe enough to demonstrate. A seeded business, helpful empty/error states, responsive QA, and early owner feedback make the project credible to both users and recruiters.

**Delivers:** Seeded demo business, focused landing page, setup guidance, responsive and accessibility pass, documentation, screenshots, deployment guide, and user testing with 3–5 Philippine service owners.

**Addresses:** Demonstrable end-to-end path, onboarding differentiator, and validation of the next most valuable capability.

**Avoids:** Building payment/staff/calendar-sync features before evidence of demand.

### Phase Ordering Rationale

- Foundation and tenancy precede all business records because changing the user model or tenant boundary after bookings/invoices exist is expensive and risks data exposure.
- Configuration and availability precede public booking because a slot must be calculated from validated business rules before the database can safely reserve it.
- Booking operations precede invoices because invoices must snapshot stable booking/customer/service facts and follow auditable lifecycle transitions.
- Reliability hardening follows a complete vertical workflow so Celery/Redis and operational complexity are introduced only where durable work/retries are demonstrably needed.
- Validation and portfolio polish close the roadmap, preserving the user-approved v1 boundary while yielding evidence for v2 priorities.

### Research Flags

Phases likely needing deeper research during planning:

- **Phase 3:** Confirm the exact v1 resource model (one default capacity versus named staff/rooms), availability edge cases, and migration support for PostgreSQL range/exclusion constraints.
- **Phase 4:** Validate the concrete idempotency, rate-limit, outbox, and email-provider patterns with the selected Django/Resend versions.
- **Phase 6:** Research Philippine invoice fields, serial-number/retention expectations, WeasyPrint/Docker font behavior, and private object-download authorization; obtain tax/legal review before compliance language.
- **Phase 7:** Verify final Render, object-storage, Redis/worker, custom-domain, and sender-domain capabilities and costs before topology is locked.

Phases with standard patterns (skip research-phase):

- **Phase 1:** Django initialization, Docker, CI, secure settings, and PostgreSQL configuration have mature official guidance.
- **Phase 2:** Custom user, membership authorization, forms, and basic multi-tenant query scoping are conventional Django patterns; focus planning on tests rather than exploratory research.
- **Phase 5:** Agenda/list/detail pages and state transitions are conventional once the scheduling command/invariant exists.
- **Phase 8:** Documentation, seeded data, responsive/accessibility QA, and structured user interviews are well-understood delivery practices.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | MEDIUM | Versions were live-checked and the main framework/deployment choices use official documentation, but exact package versions and provider capabilities must be rechecked at implementation. |
| Features | MEDIUM | Booking expectations are supported by current competitor documentation; Philippines invoice-content constraints have stronger primary BIR support. |
| Architecture | MEDIUM | Django/PostgreSQL transaction and constraint guidance is primary-source based; the exact worker rollout and resource scope are product decisions still to validate. |
| Pitfalls | MEDIUM | OWASP, Django, PostgreSQL, and BIR sources strongly support the risks, but tax/compliance interpretation requires qualified local advice. |

**Overall confidence:** MEDIUM

### Gaps to Address

- **Philippine invoice treatment:** Confirm whether and how Takdora-generated PDFs, numbering, registration, and retention meet a business's statutory duties. Do not claim BIR compliance without accountant/legal review.
- **Scheduling capacity:** The approved scope implies one business capacity in v1; decide explicitly during Phase 3 whether the internal default resource is enough or named staff/rooms are required before release.
- **Operational provider fit:** Confirm current pricing/capabilities for Render, managed Postgres/Redis, object storage, Resend sender verification, and Philippine-domain requirements when deployment planning starts.
- **User priorities:** Interview 3–5 target owners after the end-to-end flow exists to determine whether reminders, staff scheduling, deposits, or online payments deserve v2.
- **Data privacy and retention:** Define a Philippines-appropriate privacy notice, customer-data retention/deletion policy, and support process before public launch.

## Sources

### Primary (HIGH confidence)

- [PyPI JSON API](https://docs.pypi.org/api/json/) — package-version snapshots used in the stack recommendation.
- [BIR Revenue Regulations No. 7-2024](https://bir-cdn.bir.gov.ph/BIR/pdf/RR%207-2024%20%28final%29.pdf) and [RMC 77-2024 Annex A](https://orus.bir.gov.ph/files/RMC_No_77_2024_Annex_A1_B6.pdf) — Philippine invoice-content guidance.

### Secondary (MEDIUM confidence)

- [Django documentation](https://docs.djangoproject.com/en/6.1/) — deployment, transaction, query-locking, email, and framework practices.
- [PostgreSQL documentation](https://www.postgresql.org/docs/current/rangetypes.html) — range and exclusion constraints for booking non-overlap.
- [OWASP multi-tenant guidance](https://cheatsheetseries.owasp.org/cheatsheets/Multi_Tenant_Security_Cheat_Sheet.html) — tenant isolation and authorization risks.
- [Celery Django documentation](https://docs.celeryq.dev/en/stable/django/) and [Resend Python documentation](https://resend.com/docs/send-with-python) — asynchronous task and transactional email patterns.
- [Render Django deployment guide](https://render.com/docs/deploy-django), [WeasyPrint documentation](https://doc.courtbouillon.org/weasyprint/latest/first_steps.html), and current Square/Calendly product guidance — deployment, PDF rendering, and table-stakes feature expectations.

---
*Research completed: 2026-08-22*  
*Ready for roadmap: yes*
