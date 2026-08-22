param([Parameter(Mandatory = $true)] [string]$StagingUrl)

$ErrorActionPreference = 'Stop'
if ($StagingUrl -match 'production|takdora\.app') { throw 'Use an isolated staging URL, never production.' }
Invoke-WebRequest -Uri "$($StagingUrl.TrimEnd('/'))/healthz" -UseBasicParsing | Out-Null
Write-Host 'Create synthetic booking, complete it as the staging owner, issue the invoice, send its email, and verify its owner-only PDF download before promotion.'
