# Architecture Patterns

**Domain:** Configurable multi-business booking and invoicing web application  
**Researched:** 2026-08-22  
**Confidence:** MEDIUM — the critical concurrency and transaction guidance is cross-checked against current official Django and PostgreSQL documentation. Product-scale choices are informed recommendations for Takdora's v1.

## Recommended Architecture

Build Takdora as a **modular Django monolith** backed by PostgreSQL. Deploy one web process, one worker process, PostgreSQL, Redis (Celery broker), an SMTP/API email provider, and private object storage for generated PDFs. This keeps the first deployable product simple while keeping scheduling, invoices, and notifications in clearly separated Django apps.

```
Customer browser ─┐
Owner browser ────┼─> Django web app
                  │    ├─ public booking / tenant resolution
                  │    ├─ owner dashboard / authorization
                  │    ├─ scheduling domain service
                  │    └─ invoice domain service
                  └──────────────┬─────────────────────────┐
                                 v                         v
                         PostgreSQL                  Object storage
                  (tenant data + booking truth)       (private PDFs)
                                 │
                                 v
                           outbox rows ─> Celery worker ─> email provider
                                           (Redis broker)
```

Use **shared-schema multitenancy**: one database and one set of tables, with a required `business_id` foreign key on every business-owned record. It is the right v1 tradeoff: easy deployment and reporting, while reliable if every private query is explicitly scoped to the active business and every object operation verifies membership. Do not introduce schema-per-tenant databases or microservices before actual scale requires them.

### Component Boundaries

| Component | Responsibility | Communicates With |
|---|---|---|
| `accounts` | User identity, login, password reset | `tenancy`, dashboard |
| `tenancy` | `Business`, slug, profile/branding, `Membership` roles; resolves public business from URL | all tenant-aware apps |
| `catalog` | Services, prices/durations, bookable resources, business hours, breaks/closures and booking rules | `scheduling`, public page |
| `scheduling` | Computes display availability; atomically creates, cancels, and reschedules bookings | PostgreSQL, `notifications` |
| `bookings` | Customer contact snapshot, booking lifecycle/audit events | `scheduling`, dashboard, invoices |
| `billing` | Sequential invoice number, immutable issued line-item/tax snapshots, payment status, PDF request | object storage, `notifications` |
| `notifications` | Durable outbox and delivery status; renders confirmation email | Celery worker, provider |
| `dashboard` / `public` | Thin Django views/templates/forms; no booking/invoice business rules | domain services |

### Tenant Isolation Rules

1. Tenant-owned models have a non-null `business` FK and appropriate compound indexes beginning with `business_id`.
2. Dashboard URLs include a business slug, but the server derives the active business from that slug and checks an active `Membership`; never trust a posted `business_id`.
3. Expose tenant-scoped repository/queryset methods (for example, `Booking.objects.for_business(business)`) and do not use unscoped manager calls in views, forms, exports, or tasks.
4. Background tasks accept an object primary key, fetch the object, then use its stored business context. They must never accept an arbitrary tenant ID from a request.
5. Public routes may resolve only publishable booking-page configuration by slug. Customer contact data and invoice PDFs never appear on public routes.
6. Enforce object ownership at every owner operation, including direct PDF download URLs. Store PDFs privately and issue an authenticated response or short-lived signed URL.

Shared-schema isolation is primarily an application authorization boundary in v1. Add PostgreSQL row-level security only after the team can test it end-to-end with migrations, admin access, background workers, and connection pooling; partially applied RLS can create availability failures or accidental bypasses.

## Data Flow

### Customer booking

1. A public request resolves `Business` from a unique slug and reads its published services, time zone, rules, working intervals, closures, and current active bookings.
2. The availability service calculates **candidate slots** in the business time zone, then returns timestamps to the browser. Candidate slots are advisory only; the database is the final authority.
3. The submitted form validates service, duration, lead-time/advance-window rules, contact data, and an idempotency token.
4. A short `transaction.atomic()` block locks the relevant bookable resource/rule row, re-evaluates the request, and inserts a confirmed booking. PostgreSQL rejects an overlap even if another request won the race.
5. After a successful commit, create or release a durable outbox item for the confirmation email. A worker sends it and records outcome/retry state. The HTTP response confirms only the persisted booking, not speculative email delivery.

### Owner changes and invoice

1. An authenticated owner chooses a tenant context verified through `Membership`.
2. Cancellation/reschedule uses the same scheduling command and database constraint as public booking; it does not hand-edit timestamps in a dashboard view.
3. Invoice issuance copies customer, business legal details, currency, prices, taxes, and line items into immutable invoice fields. Later profile/service edits cannot alter issued records.
4. The PDF task renders from that snapshot, saves a versioned private object, and updates the invoice's PDF metadata. Marking paid is an audited state transition with date, actor, and optional reference—not deletion or a mutable free-text overwrite.

## Patterns to Follow

### Pattern 1: Tenant-first query and authorization

**What:** Resolve one business at the request boundary and pass that object into every domain command/query. Filter first by business, then by record ID.

**When:** Every dashboard route, export, upload/download, email task, and admin-like operation.

**Example:**

```python
def cancel_booking(*, business, booking_id, actor):
    booking = Booking.objects.for_business(business).get(pk=booking_id)
    assert actor.has_business_role(business, "owner")
    booking.cancelled_by = actor
    booking.status = Booking.Status.CANCELLED
    booking.save(update_fields=["cancelled_by", "status"])
```

### Pattern 2: Database-enforced non-overlap

**What:** Store all appointment timestamps as timezone-aware UTC values; model a half-open time range `[starts_at, ends_at)`. Add a PostgreSQL GiST exclusion constraint scoped to the bookable resource, with a predicate for active statuses only. Install `btree_gist` so equality on the resource can be combined with a time-range overlap check.

**When:** Before the public booking flow ships. Use one default business-level resource in v1; the same model can later support named staff/rooms without a rewrite.

**Example migration-level SQL (illustrative):**

```sql
CREATE EXTENSION IF NOT EXISTS btree_gist;

ALTER TABLE booking
ADD CONSTRAINT active_resource_time_must_not_overlap
EXCLUDE USING gist (
  resource_id WITH =,
  tstzrange(starts_at, ends_at, '[)') WITH &&
) WHERE (status IN ('confirmed', 'in_progress'));
```

PostgreSQL documents range exclusion constraints specifically for non-overlap, and `btree_gist` enables the combined scalar-equality/range test. Django's `atomic()` guarantees all-or-nothing changes, while `select_for_update()` locks selected rows only inside a transaction. Use both the constraint and a short transaction: the constraint is the final invariant; locking the resource/configuration row makes revalidation predictable. On conflict, return a friendly “that time was just taken” result and refresh availability. [PostgreSQL range constraints](https://www.postgresql.org/docs/current/rangetypes.html) · [Django transactions](https://docs.djangoproject.com/en/5.2/topics/db/transactions/) · [Django row locking](https://docs.djangoproject.com/en/5.2/ref/models/querysets/#select-for-update)

### Pattern 3: Idempotent booking submission

**What:** Render a cryptographically random, one-time booking submission key. Persist a unique `(business_id, idempotency_key)` record with the completed booking response; replays return the original result.

**When:** Public form POSTs and any future API endpoint.

**Why:** It prevents duplicate appointments when a customer double-clicks or retries after a timeout. This is separate from overlap protection: an owner could allow capacity greater than one later, but duplicate POSTs must still not create duplicate records.

### Pattern 4: Transactional outbox for email

**What:** In the same transaction that creates the booking, insert an `OutboundMessage` row (`booking_id`, template/version, recipient, state, attempts, provider ID). After commit, enqueue it; a periodic worker sweep also picks unsent rows. The worker sends idempotently and retries recoverable provider failures with backoff.

**When:** Booking confirmations and future invoice emails.

**Why:** Calling a network provider inside the booking transaction prolongs locks and can send an email for a rolled-back booking. Django’s `on_commit()` is appropriate for post-commit callbacks, but its own documentation notes callback failure cannot roll back the transaction; the persisted outbox closes the gap if enqueueing fails. Celery supports retrying recoverable work and records retry state. [Django `on_commit`](https://docs.djangoproject.com/en/5.2/topics/db/transactions/#performing-actions-after-commit) · [Celery retries](https://docs.celeryq.dev/en/stable/userguide/tasks.html#retrying)

### Pattern 5: Immutable invoice snapshot and asynchronous PDF

**What:** Issue an invoice only once its number and monetary fields are final. Save copied line-item details and business/customer information in invoice tables, enqueue a render job, and preserve the generated PDF version.

**When:** v1 invoice generation.

**Why:** A PDF must remain an accurate historical record even when a business later changes logo, address, tax settings, services, or price. Rendering can be CPU- and font-dependent, so it belongs outside the HTTP request and outside the booking transaction.

## Anti-Patterns to Avoid

### Anti-Pattern 1: Client-side or read-then-write availability

**What:** Treating a slot shown to the browser as reserved, or querying overlaps and inserting later without a database constraint.

**Why bad:** Concurrent customers can both pass the read and receive confirmation.

**Instead:** Database-enforced exclusion constraint plus a short transactional command and conflict handling.

### Anti-Pattern 2: Tenant ID from form/session without per-object checks

**What:** Filtering a list by a selected business but fetching, downloading, or changing an object solely by primary key.

**Why bad:** A guessed ID can cause cross-business data exposure or mutation.

**Instead:** Filter the target object by active business and verify membership/role before every operation.

### Anti-Pattern 3: Email/PDF work in a request transaction

**What:** Rendering a PDF or calling email before commit, or treating a successful enqueue as durable delivery.

**Why bad:** Long locks, timeouts, orphaned notifications, and confusing customer confirmations.

**Instead:** Commit domain data quickly, persist an outbox/event record, then process work asynchronously and visibly track failures.

### Anti-Pattern 4: Mutable invoices and hard deletion

**What:** Reusing an issued invoice record after correction or deleting paid/cancelled business records.

**Why bad:** Breaks auditability and makes PDFs diverge from records.

**Instead:** Status transitions, credits/voids where needed, immutable issued snapshots, and audit events.

## Scalability Considerations

| Concern | At 100 users | At 10K users | At 1M users |
|---|---|---|---|
| Tenancy | Shared schema, tenant-first indexes | Add query monitoring and archive old audit data | Evaluate RLS/partitioning or database sharding only from measured isolation/scale needs |
| Availability | Calculate on demand; one default resource | Cache only published schedule data; invalidate on schedule/booking change | Dedicated availability read model and queue-backed cache, but retain PostgreSQL as write authority |
| Booking writes | Constraint + short transaction | Tune indexes/lock timeout and use idempotency keys | Partition bookings by time/tenant only after profiling; keep conflict invariant at DB |
| Email/PDF | One worker and outbox sweep | Separate worker queues and provider metrics | Horizontally scale workers; rate limit per tenant/provider; retain replayable outbox |
| Files | Private bucket and direct authenticated response | Short-lived signed download URLs, lifecycle policies | CDN only for public assets; invoice files remain private |

## Secure Build Order

1. **Foundation and deployment:** Django settings by environment, PostgreSQL from day one, custom user model, secure production configuration, CI, backups, and error logging. Run Django’s deployment check against production settings; never commit secrets or enable production debug mode. [Django deployment checklist](https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/)
2. **Tenant boundary:** `Business`, `Membership`, role checks, tenant-scoped query helpers, private dashboard shell, and tests that prove a user in business A cannot read/change business B data.
3. **Configuration and scheduling model:** services, resources, hours, exceptions, time zone, booking rules, generated slot preview, and DST/boundary tests.
4. **Safe public booking:** form validation/rate limiting, idempotency, transactional write, exclusion constraint, concurrent-booking test, and customer confirmation outbox.
5. **Owner booking operations:** filtered calendar/list, cancellation and reschedule commands, audit events, and corresponding notification behavior.
6. **Billing:** invoice snapshot, sequential per-business number, payment-status transitions, asynchronous HTML-to-PDF render, private download authorization, and failure/retry views.
7. **Hardening/release:** email provider/domain setup, observability for outbox failures and booking conflicts, automated backups/restore drill, privacy retention policy, security headers/HTTPS, and realistic end-to-end user acceptance tests.

## Sources

- [Django 5.2 database transactions](https://docs.djangoproject.com/en/5.2/topics/db/transactions/) — MEDIUM (official primary source reached via verified web lookup)
- [Django 5.2 `select_for_update()`](https://docs.djangoproject.com/en/5.2/ref/models/querysets/#select-for-update) — MEDIUM (official primary source reached via verified web lookup)
- [Django 5.2 email](https://docs.djangoproject.com/en/5.2/topics/email/) — MEDIUM (official primary source reached via verified web lookup)
- [Django 5.2 deployment checklist](https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/) — MEDIUM (official primary source reached via verified web lookup)
- [PostgreSQL 18 range types and non-overlap constraints](https://www.postgresql.org/docs/current/rangetypes.html) — MEDIUM (official primary source reached via verified web lookup)
- [PostgreSQL 18 exclusion constraints](https://www.postgresql.org/docs/current/ddl-constraints.html) — MEDIUM (official primary source reached via verified web lookup)
- [Celery 5.6 task retrying](https://docs.celeryq.dev/en/stable/userguide/tasks.html#retrying) — MEDIUM (official primary source reached via verified web lookup)

## Open Architecture Questions

- Confirm whether v1 needs named staff/rooms or only one bookable business resource. The recommended resource abstraction supports either; do not expose extra staff-selection UX until it is a requirement.
- Choose the exact Philippine invoice/tax fields and legal retention expectations before finalizing invoice templates; this needs Philippines-specific domain and legal research.
- Confirm the deployment provider’s managed PostgreSQL, Redis, object-storage, background-worker, and custom-email-domain capabilities before selecting the production topology.
