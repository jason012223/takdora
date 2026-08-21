# Phase 1 Research: Deployable Reflex Foundation

**Researched:** 2026-08-22  
**Decision update:** The user-selected Reflex architecture supersedes the older Django-only wording in `01-CONTEXT.md` and the historical project research. Render, Docker Compose, automatic deployment from `main`, Sentry, quality gates, Playwright, coverage reporting, and dependency scanning remain locked decisions D-01 through D-08.

## Verified Technical Direction

- Reflex is a full-stack Python framework; its pages compile to browser JavaScript and server-side event handlers update state. It has a SQLModel/SQLAlchemy database integration and accepts a SQL database URL in `rxconfig.py`.
- A self-hosted Reflex production app exposes a frontend and backend separately. Render routes external traffic to only one port, so the deployment image needs a reverse proxy on `$PORT` that serves the frontend and proxies the Reflex backend/WebSocket paths. Do not expose the Reflex backend directly on a second public port.
- Render supports Docker services, `render.yaml` Blueprints, health-check paths, environment-variable secrets, linked Git branches, and automatic deployments. A health route should include a bounded database-connectivity check, returning non-success when the application cannot serve requests.
- A pull-request CI workflow can provide required checks, but GitHub branch protection itself must be enabled in the repository settings by an administrator. Document this in the operator setup guide rather than weakening the check requirement.

## Chosen Tooling

| Concern | Choice | Reason |
|---|---|---|
| Python packages | `uv` with committed `uv.lock` | Reproducible local, CI, and Docker dependency resolution. |
| App framework | `reflex[db]` | User-selected full-stack Python/Radix-based framework. |
| Database | PostgreSQL + `psycopg` | Production-safe concurrency foundation and matches D-01/D-02. |
| Tests | `pytest`, `pytest-cov`, `playwright` | Fast Python checks, CI coverage report, and D-06 browser smoke coverage. |
| Code quality | `ruff` | One formatter and linter. |
| Dependency scan | `pip-audit` | Lightweight audit of resolved Python packages for D-08. |
| Error monitoring | `sentry-sdk` | Configure only when `SENTRY_DSN` is present; preserve default PII filtering. |
| Deployment topology | Docker Compose locally; Docker + Nginx reverse proxy on Render | Matches local developer workflow and Render's one-public-port constraint. |

## Package Legitimacy Audit

| Package | Registry / official source | Intended use | Status |
|---|---|---|---|
| `reflex` | PyPI / reflex.dev | application framework | VERIFIED |
| `sqlmodel` | PyPI / sqlmodel.tiangolo.com | Reflex database model dependency | VERIFIED |
| `psycopg[binary]` | PyPI / psycopg.org | PostgreSQL driver | VERIFIED |
| `ruff` | PyPI / docs.astral.sh/ruff | lint and formatting | VERIFIED |
| `pytest` | PyPI / docs.pytest.org | test runner | VERIFIED |
| `pytest-cov` | PyPI / pytest-cov.readthedocs.io | coverage report | VERIFIED |
| `playwright` | PyPI / playwright.dev/python | browser smoke tests | VERIFIED |
| `pip-audit` | PyPI / github.com/pypa/pip-audit | dependency vulnerability scan | VERIFIED |
| `sentry-sdk` | PyPI / docs.sentry.io | error monitoring | VERIFIED |

## Implementation Constraints

- Keep `.env` files out of Git. Provide `.env.example` containing names and harmless local defaults only. Require a non-empty production secret and fail startup if it is missing.
- Define `DATABASE_URL`, `APP_ENV`, `API_URL`, `SENTRY_DSN`, and the proxy-facing port as environment settings. The public API URL must be the externally reachable Render hostname because the browser connects to the Reflex backend.
- The Docker image must run as an unprivileged user. Nginx listens on the injected high port and forwards WebSocket upgrades as well as HTTP requests.
- Avoid adding authentication, tenant models, business data, email, PDFs, or product workflow in this phase. The tracer uses a non-sensitive persistence probe only to demonstrate Reflex-to-PostgreSQL wiring.
- CI publishes coverage as an artifact and its summary but does not impose a percentage gate (D-07). The PR workflow runs `ruff format --check`, `ruff check`, unit/integration tests, browser smoke test, and `pip-audit` (D-05 through D-08).

## Sources

- [Reflex introduction](https://reflex.dev/docs/getting-started/introduction/) — full-stack Python pages, state, events, and generated browser UI.
- [Reflex database overview](https://reflex.dev/docs/database/overview/) — SQLModel integration and configurable SQL database URL.
- [Reflex self-hosting](https://reflex.dev/docs/hosting/self-hosting/) — separate production frontend/backend, API URL, and container guidance.
- [Render web services](https://render.com/docs/web-services) — Docker services, branch deploys, one public HTTP port, TLS, and WebSockets.
- [Render health checks](https://render.com/docs/health-checks) — HTTP health-check behavior and deployment readiness.
- [Render Blueprint reference](https://render.com/docs/blueprint-spec) — `healthCheckPath` and auto-deployment configuration.
- [GitHub Actions Python guide](https://docs.github.com/en/actions/tutorials/build-and-test-code/python) — Python CI workflow pattern.
