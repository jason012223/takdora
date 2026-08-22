# Local development

## Prerequisites

Install Python 3.13, [uv](https://docs.astral.sh/uv/), and Docker Desktop with its Linux container engine running.

## Start the application

1. Copy `.env.example` to `.env` and keep the local defaults, or set your own local PostgreSQL values.
2. Run `docker compose up --build`.
3. Open `http://localhost:3000` for the app and `http://localhost:8000/healthz` for the machine-readable readiness check.

The app initializes its local database migrations on startup. For a manual migration after changing models, run:

```powershell
docker compose exec app uv run reflex db makemigrations --message "describe-change"
docker compose exec app uv run reflex db migrate
```

Run focused tests with `uv run pytest tests/test_foundation.py tests/test_health.py -q`, or run the full suite with `uv run pytest`.

Stop containers with `docker compose down`. Add `--volumes` only when you intentionally want to reset local database data.

## Environment contract

`DATABASE_URL` is the private PostgreSQL SQLAlchemy URL. `API_URL` is browser-visible and must never contain credentials. `APP_SECRET_KEY` is required only in production and must be a unique, high-entropy secret. `SENTRY_DSN` is optional locally and belongs only in protected deployment configuration. `PORT` is used by the production service, not local development.

The committed `.env.example` contains only safe local defaults. `.env` and every production secret remain ignored.
