# Quality gates

GitHub Actions runs two required checks on pull requests to `main` and every push to `main`:

- **Quality** installs the frozen uv environment, checks Ruff formatting and linting, runs pytest with a coverage report, uploads `coverage.xml`, and runs `pip-audit`. Coverage is reported but has no percentage threshold.
- **Browser smoke** starts the same Docker Compose topology used locally, installs Chromium, waits for `/healthz`, and uses Playwright against the rendered application. Its reports upload only after a failure.

Browser smoke enables only the isolated synthetic fixture, then validates the marketing,
public booking, and owner-invoice narrative at 1280px and 390px. Before a production release,
run `scripts/capture-portfolio-evidence.ps1 -StagingUrl https://your-staging-origin` against
separate staging. The command stores only labelled synthetic screenshots in the gitignored
`portfolio-evidence/` directory; CI retains `playwright-report/` and `test-results/` only when
the browser check fails.

After the repository is connected to GitHub, an administrator must open **Settings → Branches → Branch protection rules → main**, require both `Quality` and `Browser smoke`, and disable direct pushes that bypass them. Repository files cannot grant that GitHub setting.
