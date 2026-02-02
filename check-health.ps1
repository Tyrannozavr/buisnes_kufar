# Health check script for development environment
Write-Host "[HEALTH CHECK] Checking development environment health..." -ForegroundColor Green
Write-Host ""

$allHealthy = $true

# Check Docker
Write-Host "[DOCKER] Checking Docker..." -ForegroundColor Yellow
$dockerRunning = docker info 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "   [OK] Docker is running" -ForegroundColor Green
} else {
    Write-Host "   [ERROR] Docker is not running" -ForegroundColor Red
    $allHealthy = $false
}

Write-Host ""

# Check Database
Write-Host "[DATABASE] Checking Database..." -ForegroundColor Yellow
$dbContainer = docker ps --filter "name=buisnes_kufar-db" --filter "status=running" -q
if ($dbContainer) {
    Write-Host "   [OK] Database container is running" -ForegroundColor Green
    # Check if database is accepting connections
    $dbCheck = docker exec buisnes_kufar-db-1 pg_isready -U postgres 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   [OK] Database is accepting connections" -ForegroundColor Green
    } else {
        Write-Host "   [WARN] Database container is running but not ready" -ForegroundColor Yellow
        $allHealthy = $false
    }
} else {
    Write-Host "   [ERROR] Database container is not running" -ForegroundColor Red
    Write-Host "      Start with: docker-compose -f docker-compose.dev.yml up -d db" -ForegroundColor Gray
    $allHealthy = $false
}

Write-Host ""

# Check RabbitMQ
Write-Host "[RABBITMQ] Checking RabbitMQ..." -ForegroundColor Yellow
$rabbitContainer = docker ps --filter "name=buisnes_kufar-rabbitmq" --filter "status=running" -q
if ($rabbitContainer) {
    Write-Host "   [OK] RabbitMQ container is running" -ForegroundColor Green
    Write-Host "      Management UI: http://localhost:15672 (admin/admin123)" -ForegroundColor Gray
} else {
    Write-Host "   [ERROR] RabbitMQ container is not running" -ForegroundColor Red
    Write-Host "      Start with: docker-compose -f docker-compose.dev.yml up -d rabbitmq" -ForegroundColor Gray
    $allHealthy = $false
}

Write-Host ""

# Check Backend
Write-Host "[BACKEND] Checking Backend..." -ForegroundColor Yellow
$backendContainer = docker ps --filter "name=buisnes_kufar-backend" --filter "status=running" -q
if ($backendContainer) {
    Write-Host "   [OK] Backend container is running" -ForegroundColor Green
    
    # Check backend API health
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8002/api/health" -Method GET -TimeoutSec 3 -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            Write-Host "   [OK] Backend API is responding" -ForegroundColor Green
            Write-Host "      API URL: http://localhost:8002/api" -ForegroundColor Gray
        }
    } catch {
        Write-Host "   [WARN] Backend container is running but API not responding" -ForegroundColor Yellow
        Write-Host "      Check logs: docker-compose -f docker-compose.dev.yml logs backend" -ForegroundColor Gray
        $allHealthy = $false
    }
} else {
    Write-Host "   [ERROR] Backend container is not running" -ForegroundColor Red
    Write-Host "      Start with: docker-compose -f docker-compose.dev.yml up -d backend" -ForegroundColor Gray
    $allHealthy = $false
}

Write-Host ""

# Check Celery Worker
Write-Host "[CELERY] Checking Celery Worker..." -ForegroundColor Yellow
$celeryContainer = docker ps --filter "name=buisnes_kufar-celery-worker" --filter "status=running" -q
if ($celeryContainer) {
    Write-Host "   [OK] Celery worker is running" -ForegroundColor Green
} else {
    Write-Host "   [WARN] Celery worker is not running" -ForegroundColor Yellow
    Write-Host "      Start with: docker-compose -f docker-compose.dev.yml up -d celery-worker" -ForegroundColor Gray
}

Write-Host ""

# Check Frontend (local or Docker)
Write-Host "[FRONTEND] Checking Frontend..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3000" -Method GET -TimeoutSec 3 -ErrorAction Stop
    if ($response.StatusCode -eq 200) {
        Write-Host "   [OK] Frontend is responding" -ForegroundColor Green
        Write-Host "      Frontend URL: http://localhost:3000" -ForegroundColor Gray
    }
} catch {
    Write-Host "   [ERROR] Frontend is not responding on port 3000" -ForegroundColor Red
    Write-Host "      Start locally: cd frontend && npm run dev" -ForegroundColor Gray
    $allHealthy = $false
}

Write-Host ""
Write-Host "=======================================================" -ForegroundColor Cyan

if ($allHealthy) {
    Write-Host "[SUCCESS] All critical services are healthy!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Ready to develop!" -ForegroundColor Cyan
    Write-Host "   Frontend: http://localhost:3000" -ForegroundColor White
    Write-Host "   Backend API: http://localhost:8002/api" -ForegroundColor White
    Write-Host "   API Docs: http://localhost:8002/docs" -ForegroundColor White
} else {
    Write-Host "[WARN] Some services are not running properly" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Quick start all services:" -ForegroundColor Cyan
    Write-Host "   .\dev-local.ps1" -ForegroundColor White
}

Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host ""
