# Script to create multiple test users with companies and products for development
# This bypasses email verification for quick testing

Write-Host "[TEST DATA] Creating test users, companies and products for development..." -ForegroundColor Green

# Check if database is running
Write-Host ""
Write-Host "[CHECK] Checking if database is running..." -ForegroundColor Yellow
$dbRunning = docker ps --filter "name=buisnes_kufar-db" --filter "status=running" -q
if (-not $dbRunning) {
    Write-Host "[ERROR] Database container is not running!" -ForegroundColor Red
    Write-Host "   Starting database..." -ForegroundColor Yellow
    docker-compose -f docker-compose.dev.yml up -d db
    Write-Host "   Waiting for database to be ready..." -ForegroundColor Yellow
    Start-Sleep -Seconds 5
}

Write-Host "[OK] Database is ready" -ForegroundColor Green

# Run the Python script to create test data
Write-Host ""
Write-Host "[PYTHON] Running Python script to create test data..." -ForegroundColor Yellow

# Change to backend directory
Push-Location -Path "backend"

try {
    # Run the script using Python from the backend Docker container
    Write-Host ""
    Write-Host "Using backend container to create test users, companies and products..." -ForegroundColor Cyan
    docker-compose -f ../docker-compose.dev.yml exec -T backend poetry run python create_test_user.py
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "[SUCCESS] Test data created! You can now login at http://localhost:3001/auth/login" -ForegroundColor Green
        Write-Host "          Password for all test users: Test123!" -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host "[WARN] Script completed with warnings. Check the output above." -ForegroundColor Yellow
    }
} catch {
    Write-Host ""
    Write-Host "[ERROR] Error running script: $_" -ForegroundColor Red
} finally {
    Pop-Location
}
