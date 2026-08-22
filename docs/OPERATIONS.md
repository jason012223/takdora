# Takdora Operations Runbook

## Health and incident triage

`GET /healthz` is the service readiness endpoint. It returns `200` with
`{"status":"ok"}` only when the configured PostgreSQL connection can complete a
small query. It returns `503` with `{"status":"unavailable"}` when the database
cannot be reached; it never returns exception text or configuration values.

Render uses this endpoint to decide whether a new deployment receives traffic.
If it fails:

1. Check the current Render deploy logs for migration and backend-startup errors.
2. Check Render PostgreSQL availability and its private connection reference.
3. Check the Sentry issue metadata for a release/environment trend; do not paste
   DSNs, request bodies, customer notes, or database URLs into incident tickets.
4. Roll back to the last healthy application deploy if the failure followed a
   release. Do not roll back a database schema without an explicit recovery plan.

## Email and PDF delivery failures

Later Takdora phases surface delivery failures to the owner with a retry action
and alert the operator. Until those workflows exist, use Render logs and Sentry
to investigate application errors. Do not mark an appointment or invoice failed
solely because delivery failed: preserve the record and provide a safe retry.

## Planned maintenance

Set the protected Render environment value `MAINTENANCE_MODE=true`, deploy, and
open the root page. Visitors receive Takdora's bounded maintenance page while
`/healthz` continues to report application readiness for Render. The page never
contains a bypass URL, configuration, or customer data. After the maintenance
window, set `MAINTENANCE_MODE=false`, deploy, then verify both `/healthz` and the
root page before announcing that service is restored.

## Backups and recovery

Configure Render PostgreSQL backups according to the chosen Render plan before
accepting real business data. Periodically rehearse restoring a backup into a
separate non-production database; never test recovery against the live database.
Record the recovery time and any migration version needed for restoration.

## Staging and releases

Before each production release, deploy the same image to a separate staging
service with non-sensitive test data. Run the booking-to-invoice smoke flow,
then merge only after the GitHub checks pass. Production receives deployments
from `main` only; staging must never use production credentials or customer data.
