param(
  [Parameter(Mandatory = $true)] [string]$StagingUrl,
  [Parameter(Mandatory = $true)] [string]$BackupEvidencePath
)

$ErrorActionPreference = 'Stop'
if ($StagingUrl -match 'production|takdora\.app') { throw 'Use an isolated staging URL, never production.' }
if (-not (Test-Path -LiteralPath $BackupEvidencePath)) { throw 'A non-production backup-and-restore evidence file is required.' }
uv run ruff format --check .
uv run ruff check .
uv run pytest
uv run reflex db migrate
$health = Invoke-RestMethod -Uri "$($StagingUrl.TrimEnd('/'))/healthz" -Method Get
if ($health.status -ne 'ok') { throw 'Staging health check did not return status ok.' }
Write-Host 'Release gate passed: quality, migrations, backup evidence, and staging health are verified.'
