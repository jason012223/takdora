# Takdora portfolio guide

Takdora is a configurable booking and invoice hub for Philippine service businesses.
The live home page guides prospective owners to **Create your business**; the optional
`/demo` route is a clearly labelled synthetic workspace for portfolio review.

## Reviewer flow

1. Open the staging home page and choose **Try the demo**.
2. Confirm the synthetic-data label before opening the synthetic public business.
3. Enter the synthetic owner workspace to inspect its completed booking, issued invoice,
   and partially paid manual-payment example.

The demo uses only resettable `takdora.example` contacts and suppresses external delivery.
It must be enabled only in staging through `SYNTHETIC_DEMO_ENABLED=true`, never production.

## Evidence and release checks

Run `scripts/capture-portfolio-evidence.ps1 -StagingUrl https://your-staging-origin` from
PowerShell after configuring isolated staging. The command refuses the production origin,
writes gitignored screenshots to `portfolio-evidence/`, and prints only capture paths.

The responsive browser checks run the public marketing, booking, and owner flows at 1280px
and 390px through the Docker Compose service network. CI retains Playwright failure output.

## V1 boundaries

- Payments are manually tracked by the owner; Takdora does not process online payments.
- Owners manage booking changes; customers do not have accounts or self-service changes.
- Invoice PDFs are configurable and BIR-aware, but are not represented as BIR-compliant,
  registered e-invoices, or sales-reporting output.
- The production deployment is a single Render service with PostgreSQL and private object
  storage configuration; source control checks must pass before a deployment from `main`.
