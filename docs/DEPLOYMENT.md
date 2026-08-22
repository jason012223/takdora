# Deploying Takdora to Render

Takdora deploys one Docker web service from the repository's `main` branch. The
service runs Nginx on Render's injected `PORT`; Nginx serves the exported Reflex
frontend and proxies `/api/` (including WebSocket upgrades) and `/healthz` to the
private Reflex backend. PostgreSQL stays on Render's private network.

## Before the first deploy

1. Push this repository to GitHub and make `main` the production branch.
2. In Render, select **New > Blueprint**, connect the repository, and apply
   `render.yaml` in the Singapore region (or change the database and service to
   the same preferred region before creating it).
3. Render creates `takdora` and `takdora-postgres`. Keep the generated
   `APP_SECRET_KEY`; it is a protected Render secret and must never be copied to
   the repository or browser.
4. Set `API_URL` in the service Environment panel to the public HTTPS service
   URL followed by `/api`, for example
   `https://takdora.onrender.com/api`. This cannot be derived in `render.yaml`
   because Blueprint files do not interpolate variables.
5. Create a new Sentry project. Add its DSN as the protected `SENTRY_DSN`
   environment value. Leave it empty only if error monitoring is intentionally
   not enabled yet.
6. Confirm `DATABASE_URL` references the `takdora-postgres` internal connection
   string. Never replace it with a public connection URL.

The image validates production configuration on startup, applies existing
database migrations, exports the frontend, then starts the backend and reverse
proxy. Do not include credentials in a Docker build argument or GitHub secret
used by the image build.

## First-deploy verification

After Render reports a successful deploy:

1. Open `https://<service>.onrender.com/healthz` and expect `{"status":"ok"}`.
2. Open the root page and use the readiness control. It should report success
   without exposing database URLs or configuration values.
3. In Render Logs, confirm the service is listening on the injected `PORT` and
   no migration error occurred.
4. Trigger one non-sensitive test exception only in a non-production environment
   to verify Sentry. Never use a customer booking or invoice to test monitoring.

## Release policy and rollback

Render automatic deployment is set to `checksPass` for `main`. Keep GitHub's
**Quality** and **Browser smoke** checks required before a merge to `main`.
If a healthy deployment behaves incorrectly, open **Render > takdora > Events**,
choose the last known-good deploy, and use **Rollback**. Re-check `/healthz` and
the root page after the rollback. Database migrations must remain backward
compatible with the previous application release before merging.

## Required human-owned setup

The project owner must authorize Render and Sentry, connect the GitHub
repository, supply `API_URL` and `SENTRY_DSN`, and approve the first deployment.
This repository deliberately cannot create those accounts or access their
secrets.

## Staging release gate

Apply `render.staging.yaml` to a separate Render environment and configure a
different database, object-storage bucket or prefix, sender, Sentry DSN, and
credentials. Never copy a production resource into staging. Before merging to
`main`, record one restore drill into a non-production database, then run:

```powershell
.\scripts\release-check.ps1 -StagingUrl https://<staging-service> -BackupEvidencePath .\private\staging-restore-evidence.txt
```

For a Windows Docker browser check that does not rely on forwarded ports, run:

```powershell
docker compose -f compose.yaml -f compose.e2e.yaml run --rm e2e uv run pytest tests/e2e/test_foundation_smoke.py -q
```
