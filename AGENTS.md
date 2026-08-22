# Takdora project instructions

Takdora is a configurable booking and invoicing hub for Philippine service businesses. Keep the product multi-tenant, privacy-conscious, and usable on mobile.

## Foundation stack

- Python 3.13 with `uv` for dependency management and locked `uv.lock` installs.
- Reflex with its Radix-based components for the full-stack web app; do not add Django, HTMX, or a separate SPA.
- PostgreSQL 17 through Reflex SQLModel models and migrations; never use SQLite for production behavior.
- Docker Compose for local development and a single Docker service on Render for production.
- Run `uv run ruff format --check .`, `uv run ruff check .`, and `uv run pytest` before committing code.

## Security and operations

- Never commit `.env` files, database URLs, API keys, Sentry DSNs, or production credentials.
- Read configuration from environment variables. Browser-visible URLs must never contain credentials.
- Scope every business query and mutation to its owner/workspace once tenancy is introduced.
- Keep public health responses machine-readable and free of stack traces or configuration values.
- Use `Decimal`/database decimal fields for money. Store times in UTC and retain an IANA business timezone.
- Production deploys are from `main` through Render only after the required GitHub checks pass.

## Workflow

Use GSD phase workflows for planned changes. Preserve planning artifacts and do not revert other agents' changes.
