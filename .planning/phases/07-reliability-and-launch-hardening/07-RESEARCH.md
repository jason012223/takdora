# Phase 7 Research: Reliability and Launch Hardening

## Chosen implementation approach

- Keep the existing database outboxes as the source of delivery truth. A due-delivery processor locks one record, increments its attempt count, and records either an idempotent sent result or a bounded delayed/failed result. It must never modify a booking or invoice state when an email or PDF action fails.
- Use private S3-compatible object storage through `boto3` for logos and issued PDFs. Store only opaque object keys plus metadata in PostgreSQL. Owner downloads pass through a server-side authorization check and receive a short-lived, response-disposition-bound presigned URL; storage objects remain private and no public object URL is persisted.
- Run a dedicated Render staging service and database with only synthetic seed data. A release check validates migration head, asset export, health, backup/recovery evidence, configuration shape, the public booking-to-invoice path, email delivery state, and owner-authorized PDF access before production receives a main-branch deployment.
- Use a container-network Playwright runner for browser checks. This removes the existing Windows/Docker Desktop host-port limitation by addressing the Reflex frontend and backend through the Compose service network rather than host loopback.

## Constraints

- The booking confirmation contract remains: a committed appointment is confirmed even when confirmation email delivery is delayed. Retrying must not create another booking or send duplicate notifications after a sent state is recorded.
- Invoice issuance is a Phase 6 precondition. Phase 7 migrates the established `InvoiceDocument.content` bytes to storage-backed `storage_key` metadata and preserves the one-document-per-invoice constraint.
- Business storage keys are generated on the server from a non-guessable UUID, scoped by business ID, and never accepted from the browser. Uploaded logos are content-type and byte-size validated before write.
- Monitoring records only bounded technical codes, record IDs, and business IDs; it does not emit customer email, customer note, invoice content, SMTP configuration, or object-storage credentials.
- Render `sync: false` environment values are populated by the operator in the matching environment; staging must use a separate database, storage prefix/bucket, sender, and secrets.

## Package Legitimacy Audit

| Package | Version range | Registry / primary source | Status | Why |
|---|---|---|---|---|
| boto3 | `>=1.40,<2.0` | https://pypi.org/project/boto3/ | VERIFIED | Official AWS SDK for Python; its S3 client creates short-lived presigned URLs and supports S3-compatible object storage. |

## Sources

- [Boto3 presigned URL guide](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-presigned-urls.html) - official SDK guidance for time-limited S3 access.
- [Render Blueprint reference](https://render.com/docs/blueprint-spec) - official service, database, environment, and secret declaration behavior.
- [Render projects and environments](https://render.com/docs/projects) - staging/production separation and cross-environment safeguards.
- [Render Postgres recovery and backups](https://render.com/docs/postgresql-backups) - logical backup retention and recovery workflow.

