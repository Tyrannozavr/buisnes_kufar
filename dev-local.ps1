# Development script for local frontend + Docker backend
Write-Host "[START] Starting development environment (local frontend + Docker backend)" -ForegroundColor Green

# Check if Docker is running
Write-Host ""
Write-Host "[DOCKER] Checking Docker..." -ForegroundColor Yellow
$dockerRunning = docker info 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Docker is not running. Please start Docker Desktop and try again." -ForegroundColor Red
    exit 1
}

Write-Host "[OK] Docker is running" -ForegroundColor Green

# Start backend services
Write-Host ""
Write-Host "[DOCKER] Starting backend services in Docker..." -ForegroundColor Yellow
docker-compose -f docker-compose.dev.yml up -d db rabbitmq backend celery-worker celery-beat

# Wait for services to be healthy
Write-Host ""
Write-Host "[WAIT] Waiting for backend to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Check backend health
$backendHealthy = $false
$attempts = 0
while (-not $backendHealthy -and $attempts -lt 30) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8002/api/health" -Method GET -TimeoutSec 2 -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            $backendHealthy = $true
        }
    } catch {
        Start-Sleep -Seconds 2
        $attempts++
    }
}

if ($backendHealthy) {
    Write-Host "[OK] Backend is ready!" -ForegroundColor Green
} else {
    Write-Host "[WARN] Backend might not be fully ready yet, but continuing..." -ForegroundColor Yellow
}

# Start frontend
Write-Host ""
Write-Host "[FRONTEND] Starting frontend locally..." -ForegroundColor Yellow
Write-Host "   Frontend will run at: http://localhost:3000" -ForegroundColor Cyan
Write-Host "   Backend API is at: http://localhost:8002" -ForegroundColor Cyan
Write-Host ""
Write-Host "[READY] Development environment is ready!" -ForegroundColor Green
Write-Host ""
Write-Host "To view backend logs: docker-compose -f docker-compose.dev.yml logs -f backend" -ForegroundColor Gray
Write-Host "To stop backend: docker-compose -f docker-compose.dev.yml down" -ForegroundColor Gray
Write-Host ""

# Change to frontend directory and start dev server
Set-Location -Path "frontend"
npm run dev
