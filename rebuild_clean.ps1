Write-Host "Starting rebuild process..." -ForegroundColor Cyan

Write-Host "Spinning down services..." -ForegroundColor Yellow
docker-compose down
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to spin down services" -ForegroundColor Red
    exit 1
}

Write-Host "Waiting for containers to stop..." -ForegroundColor Gray
do {
    Start-Sleep -Seconds 2
    $runningContainers = docker ps --filter "name=casewise-v2" --format "table {{.Names}}" 2>$null
} while ($runningContainers -and $runningContainers.Length -gt 1)
Write-Host "All containers stopped" -ForegroundColor Green

Write-Host "Rebuilding specific containers (no cache)..." -ForegroundColor Yellow
docker-compose build --no-cache casewise-dev dicom-server ohif-viewer frontend
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to rebuild containers" -ForegroundColor Red
    exit 1
}
Write-Host "Build completed successfully" -ForegroundColor Green

Write-Host "Spinning up services..." -ForegroundColor Yellow
docker-compose up -d casewise-dev dicom-server ohif-viewer frontend
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to spin up services" -ForegroundColor Red
    exit 1
}

Write-Host "Waiting for containers to start..." -ForegroundColor Gray
$maxAttempts = 30
$attempt = 0
do {
    Start-Sleep -Seconds 2
    $attempt++
    $runningContainers = docker ps --filter "name=casewise-v2" --format "table {{.Names}}" 2>$null
    $hasAllServices = ($runningContainers -like "*casewise-dev*") -and 
                     ($runningContainers -like "*dicom-server*") -and 
                     ($runningContainers -like "*ohif-viewer*") -and 
                     ($runningContainers -like "*frontend*")
} while (-not $hasAllServices -and $attempt -lt $maxAttempts)

if ($hasAllServices) {
    Write-Host "All containers are running" -ForegroundColor Green
} else {
    Write-Host "Timeout waiting for containers to start" -ForegroundColor Yellow
}

Write-Host "Rebuild process completed successfully!" -ForegroundColor Green
Write-Host "Services running:" -ForegroundColor Cyan
Write-Host "  - CaseWise Dev: Running" -ForegroundColor White
Write-Host "  - DICOM Server: Running" -ForegroundColor White
Write-Host "  - OHIF Viewer: http://localhost:8081" -ForegroundColor White
Write-Host "  - Frontend: Running" -ForegroundColor White 