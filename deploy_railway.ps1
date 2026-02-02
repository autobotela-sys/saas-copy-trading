# Railway Deployment Script
$ErrorActionPreference = "Stop"

$project = "5fad707a-bcd2-4fb6-805f-282da19a459a"
$env = "6a3e066a-0a24-49af-a509-737c33ee1c4b"
$repo = "autobotela-sys/saas-copy-trading"

# Link project
Write-Host "Linking Railway project..."
railway link --project $project --environment $env

# Add PostgreSQL
Write-Host "Adding PostgreSQL..."
$railwayPath = "C:\Users\elamuruganm\AppData\Roaming\npm\railway.cmd"
& $railwayPath add -d postgres

# Wait for PostgreSQL
Write-Host "Waiting 20 seconds for PostgreSQL to provision..."
Start-Sleep -Seconds 20

# Add backend service
Write-Host "Adding backend service..."
& $railwayPath add -r $repo -s backend

# Add frontend service
Write-Host "Adding frontend service..."
& $railwayPath add -r $repo -s frontend

Write-Host "Deployment initiated!"
