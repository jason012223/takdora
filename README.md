# Takdora

Takdora is a configurable booking and invoice hub for Philippine small service businesses. It gives an owner one clear path: publish a booking page, manage the appointment, issue a PDF invoice, then record payment manually.

> V1 does not accept online payments. Invoice records are configurable and BIR-aware, but Takdora does not claim to provide BIR-registered e-invoicing, sales reporting, or tax determination.

## What it includes

- A public, account-free booking page with services, available dates and local-time slots.
- A private owner workspace for business setup, services, hours, bookings, and invoices.
- Completion-to-invoice workflow, PDF generation, email delivery status, and manual payment tracking.
- A resettable synthetic demo for portfolio review; it never uses real customer data or sends visitor email.
- Tenant-scoped server commands, PostgreSQL persistence, accessibility-oriented Radix UI, and health checks.

## Stack

Python 3.13, [Reflex](https://reflex.dev/) with Radix components, PostgreSQL, SQLModel/SQLAlchemy, Docker Compose, Playwright, Ruff, pytest, and Render deployment configuration.

## Run locally

1. Install Python 3.13, [uv](https://docs.astral.sh/uv/), and Docker Desktop.
2. Copy `.env.example` to `.env`.
3. Run `docker compose up --build`.
4. Open `http://localhost:3000`; use `http://localhost:8000/healthz` for readiness.

To inspect the resettable portfolio scenario locally, add `SYNTHETIC_DEMO_ENABLED=true` to your ignored `.env` and open `/demo`.

Run the checks:

```powershell
uv run ruff format --check .
uv run ruff check .
uv run pytest -q
```

## Documentation

- [Local development](docs/LOCAL-DEVELOPMENT.md)
- [Deployment to Render](docs/DEPLOYMENT.md)
- [Operations runbook](docs/OPERATIONS.md)
- [Quality gates](docs/QUALITY.md)
- [Portfolio demo guide](docs/PORTFOLIO.md)
- [Product scope and boundaries](PRODUCT.md)

## Deployment and ownership

The included `render.yaml` provisions the application and PostgreSQL shape, but the repository owner must connect GitHub to Render and configure the protected production values described in the deployment guide. Do not commit `.env`, database URLs, Sentry DSNs, or object-storage credentials.

## License

No license has been selected yet. Add one before accepting outside contributions or reuse.
