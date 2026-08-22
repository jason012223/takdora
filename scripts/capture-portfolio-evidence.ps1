param(
    [Parameter(Mandatory = $true)]
    [ValidatePattern('^https://')]
    [string]$StagingUrl,
    [string]$EvidenceDirectory = 'portfolio-evidence'
)

$ErrorActionPreference = 'Stop'

if ($StagingUrl -match '(^|\.)takdora\.app($|/)') {
    throw 'Refusing to capture portfolio evidence from the production origin.'
}

$resolvedEvidenceDirectory = Join-Path (Get-Location) $EvidenceDirectory
New-Item -ItemType Directory -Force -Path $resolvedEvidenceDirectory | Out-Null

$env:TAKDORA_TEST_BASE_URL = $StagingUrl.TrimEnd('/')
$env:TAKDORA_TEST_HEALTH_URL = "$($env:TAKDORA_TEST_BASE_URL)/healthz"
$env:TAKDORA_EVIDENCE_DIR = '/evidence'

docker compose -f compose.yaml -f compose.e2e.yaml run --rm `
    -v "${resolvedEvidenceDirectory}:/evidence" `
    e2e uv run pytest tests/e2e/test_marketing_smoke.py tests/e2e/test_portfolio_workflow_smoke.py -q

Get-ChildItem -File $resolvedEvidenceDirectory -Filter '*.png' |
    ForEach-Object { Write-Output "PASS $($_.FullName)" }
