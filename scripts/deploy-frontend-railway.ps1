# Deploy frontend to Railway from local saas_app/frontend (fixes root directory / GitHub path issues).
# Run from repo root: .\saas_app\scripts\deploy-frontend-railway.ps1
# Requires: railway login, railway link -p copy-trading-saas -s frontend

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$frontendPath = Join-Path $root "frontend"
if (-not (Test-Path (Join-Path $frontendPath "package.json"))) {
    Write-Error "Frontend not found at $frontendPath"
}
Push-Location $root
try {
    railway up saas_app/frontend --path-as-root -s frontend -d
} finally {
    Pop-Location
}
