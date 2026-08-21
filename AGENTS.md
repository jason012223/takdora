<!-- GSD:project-start source:PROJECT.md -->

## Project

**Takdora**

Takdora is a web-based booking and invoicing hub for configurable service businesses in the Philippines, such as salons, tutors, freelancers, and repair providers. Each business receives a public booking page for customers and a private dashboard to manage services, schedules, bookings, and invoices.

**Core Value:** Make it effortless for a service business to accept a customer booking and track the resulting invoice in one dependable place.

### Constraints

- **Market**: Philippines-first — defaults should suit local small service businesses while remaining adaptable.
- **Product scope**: Configurable multi-business platform — avoid hard-coding assumptions for salons, tutors, or any single sector.
- **Payments**: Manual payment-status workflow only in v1 — avoid payment-provider complexity before validating core operations.
- **Deployment**: Publicly deployable web application — the finished project must be usable by real people, not only a local demo.
- **Security**: Public booking and private business data require authorization, tenant isolation, and safe handling of customer data.

<!-- GSD:project-end -->

<!-- GSD:stack-start source:research/STACK.md -->

## Technology Stack

## Recommendation

### Core Framework

| Technology | Version | Purpose | Why |
|---|---:|---|---|
| Python | 3.13 | Runtime | Modern supported runtime; satisfies Django 6.1's Python >=3.12 requirement. Pin the exact patch version in `.python-version`/Docker and upgrade deliberately. |
| Django | 6.1 | Full-stack web application | Mature batteries-included fit for a public booking workflow: models, database transactions, auth, admin, templates, forms, i18n/time zones, security settings, and migrations. |
| Django templates | bundled | Public booking pages and owner dashboard | Keeps customer pages, form validation, authorization, and rendering in one codebase. Use a component-like `templates/components/` convention. |
| HTMX | 2.0.10 | Small progressive-interaction layer | Use for availability-slot refreshes, modal/detail panels, and inline status updates without operating a separate SPA/API. Serve the pinned static file locally. |
| django-htmx | 1.29.0 | Django/HTMX integration | Adds request helpers and middleware; use wherever HTMX responses are needed. |
| Bootstrap | 5.3.8 | Responsive UI primitives | Provides dependable accessible form, grid, modal, and navigation primitives for a portfolio app without designing a component system from scratch. Customize with Takdora tokens; do not ship its default visual style. |

### Database and Persistence

| Technology | Version | Purpose | Why |
|---|---:|---|---|
| PostgreSQL | 17 | Primary relational datastore | Correct choice for bookings/invoices: transactions, uniqueness/exclusion constraints, indexes, JSON only where appropriate, and reliable backups. Use a managed instance in the same Render region as the app. |
| psycopg | 3.3.4 | PostgreSQL driver | Current Django-compatible PostgreSQL driver. Install `psycopg[binary]` for the containerized application. |
| django-storages | 1.14.6 | Object-storage integration | Store immutable generated invoice PDFs and business logo uploads outside the ephemeral web filesystem. |
| boto3 | 1.43.77 | S3-compatible storage client | Backend for django-storages. Use Cloudflare R2 or AWS S3; choose R2 for low-cost early storage and migrate only if requirements demand AWS. |

### Production Infrastructure

| Technology | Version | Purpose | Why |
|---|---:|---|---|
| Docker | 27+ | Repeatable build/runtime | Necessary to make WeasyPrint's native Pango/font dependencies reproducible and to keep local/CI/production runtime parity. Build from a slim Debian Python image, run as a non-root user. |
| Gunicorn | 26.1.0 | Production process manager | Stable multi-worker WSGI/ASGI process manager. |
| Uvicorn | 0.52.4 | ASGI worker | Run `gunicorn takdora.asgi:application -k uvicorn.workers.UvicornWorker`; it supports normal HTTP now and permits later async work without replacing deployment. |
| Render Web Service | managed | Public application hosting | Official Django blueprint and managed Postgres documentation make deployment straightforward. Use a paid always-on instance for actual users: Render's free web services spin down after 15 minutes. |
| Render Postgres | managed | Production DB, backups and recovery | Use its internal connection URL from an app in the same account/region; public DB URLs are slower and unnecessary. |
| GitHub Actions | current hosted runner | CI | Run `ruff check`, `ruff format --check`, Django tests, migration consistency and `python manage.py check --deploy` before merging. |
| Sentry Python SDK | 2.68.0 | Error monitoring | Capture production exceptions with release and request context. Configure before public launch; do not send customer PII in custom tags. |

### Supporting Libraries

| Library | Version | Purpose | When to use |
|---|---:|---|---|
| WeasyPrint | 69.0 | Generate PDF invoices from server-controlled HTML/CSS | Use a fixed invoice template and trusted logo URL handling. Bake Pango/font packages into the Docker image. Regression-test representative PDFs when upgrading, because rendering output can change across WeasyPrint releases. |
| Resend | 2.39.0 | Transactional booking-confirmation email | Use after verifying a Takdora sending domain. Send from a named business address only after that business's domain is verified; otherwise use a Takdora sender/reply-to flow. |
| Celery | 5.6.3 | Background jobs | Add for reliable retryable email, scheduled reminders and slow PDF work after core booking works. Django support is built in. |
| redis | 8.1.0 | Redis client | Add alongside Celery as broker/result backend only when Celery is introduced. Use managed Redis; do not expose it publicly. |
| django-ratelimit | 4.1.0 | Public endpoint abuse controls | Rate-limit booking submission and login/reset endpoints by IP and, where useful, email/business slug. |
| Whitenoise | 6.12.0 | Static asset serving | Fine for CSS/JS/static assets on a single Render service. Do **not** use it for customer uploads or invoice files. |
| Pillow | 12.3.0 | Validate/process logo image uploads | Enforce file type, dimensions and size before storage. |
| ruff | 0.16.4 | Linting and formatting | Use as the single fast lint/format tool. |
| pytest + pytest-django | 9.1.1 / 4.14.0 | Tests | Focus tests on appointment availability, tenant isolation, authorization, invoice totals/status, and confirmation-email behavior. |

## Specific Implementation Choices

- Use `zoneinfo.ZoneInfo("Asia/Manila")` as the initial business default but persist an IANA time-zone string per business. Store appointment instants in UTC; display them in the business time zone.
- Use `Decimal` and integer centavos (or `DecimalField` with explicitly chosen precision) for invoice money; never `float`.
- Use a custom Django `User` model in the first migration. An owner can later belong to multiple businesses through an explicit membership model.
- Send confirmations only via `transaction.on_commit()` so a mail request never describes a booking that later rolls back. Celery tasks must receive IDs, re-query data, and be idempotent.
- Generate each final invoice once, persist its invoice number, line items/totals snapshot, PDF object key, and status. Never recompute a historical invoice from subsequently edited services or business details.
- Keep app secrets (`SECRET_KEY`, database URL, S3 credentials, Resend key, Sentry DSN) in Render environment variables, never in the repo. Set `DEBUG=False`, correct `ALLOWED_HOSTS`/`CSRF_TRUSTED_ORIGINS`, secure cookies, HTTPS redirects, and run Django's deployment checks.

## Alternatives Considered

| Category | Recommended | Alternative | Why not for v1 |
|---|---|---|---|
| Web framework | Django monolith | FastAPI + React/Next | Excellent for API-first systems, but creates two apps plus auth, admin, validation and authorization seams. Takdora needs a working product fast, not an API platform. |
| UI approach | Templates + HTMX + Bootstrap | SPA | Customer booking is mostly standard forms; an SPA increases bundle, API, state, routing and deployment complexity before real needs are known. |
| Database | Managed PostgreSQL | SQLite/MySQL | SQLite is unsuitable for a concurrent public booking service; PostgreSQL provides the safest future path for concurrency constraints. MySQL brings no advantage here. |
| PDF generation | WeasyPrint | wkhtmltopdf / browser automation | wkhtmltopdf has an aging rendering engine and headless browser PDF brings a larger runtime. WeasyPrint directly renders print CSS and documents invoice use. |
| Async queue | Celery + Redis only when needed | Celery from day one / serverless tasks | A queue is justified for retries and scheduled work, but it adds worker and broker operations. Do not block the first public workflow on it. |
| Email | Resend | Gmail SMTP | Resend has a maintained Python integration, domain verification and transactional focus. Consumer SMTP is a weak production delivery path. |
| Tenant isolation | Shared database + strict organization scoping | `django-tenants` schemas | Schema tenancy complicates migrations, admin/reporting and backups with little early-stage benefit. Move only if contractual isolation requirements appear. |
| File storage | S3-compatible object storage | Render disk / database blobs | Render's normal service filesystem is ephemeral, and database blobs make backups and response paths worse. |
| Deployment | Render + Docker | A free-only host | Free instances sleep and are not suitable for dependable booking confirmation; a paid always-on service is part of a real deployment. |

## Installation Baseline

# Add only with asynchronous delivery/reminders:

## Sources

- [Django download/release documentation](https://www.djangoproject.com/download/) and [Django deployment checklist](https://docs.djangoproject.com/en/6.1/howto/deployment/checklist/) — MEDIUM (official docs; live PyPI also verified Django 6.1 and Python requirement).
- [django-allauth documentation](https://docs.allauth.org/en/latest/) and [release notes](https://docs.allauth.org/en/latest/release-notes/index.html) — MEDIUM.
- [Celery's Django documentation](https://docs.celeryq.dev/en/stable/django/) — MEDIUM.
- [WeasyPrint first steps and security guidance](https://doc.courtbouillon.org/weasyprint/latest/first_steps.html) — MEDIUM.
- [Resend Python email documentation](https://resend.com/docs/send-with-python) — MEDIUM.
- [Render's Django deployment guide](https://render.com/docs/deploy-django), [Render Postgres connections](https://render.com/docs/postgresql-creating-connecting), and [service filesystem/deploy behavior](https://render.com/docs/deploys) — MEDIUM.
- [PyPI JSON API](https://docs.pypi.org/api/json/) package metadata queried live for the listed Python package versions — HIGH for version snapshots.

<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->

## Conventions

Conventions not yet established. Will populate as patterns emerge during development.
<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->

## Architecture

Architecture not yet mapped. Follow existing patterns found in the codebase.
<!-- GSD:architecture-end -->

<!-- GSD:skills-start source:skills/ -->

## Project Skills

No project skills found. Add skills to any of: `.claude/skills/`, `.agents/skills/`, `.cursor/skills/`, `.github/skills/`, or `.codex/skills/` with a `SKILL.md` index file.
<!-- GSD:skills-end -->

<!-- GSD:workflow-start source:GSD defaults -->

## GSD Workflow Enforcement

Before using Edit, Write, or other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.

Use these entry points:

- `/gsd-quick` for small fixes, doc updates, and ad-hoc tasks
- `/gsd-debug` for investigation and bug fixing
- `/gsd-execute-phase` for planned phase work

Do not make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it.
<!-- GSD:workflow-end -->

<!-- GSD:profile-start -->

## Developer Profile

> Profile not yet configured. Run `/gsd-profile-user` to generate your developer profile.
> This section is managed by `generate-claude-profile` -- do not edit manually.
<!-- GSD:profile-end -->
