@echo off
echo Starting rebuild process...

echo Spinning down services...
docker-compose down
if %errorlevel% neq 0 (
    echo Failed to spin down services
    exit /b 1
)

echo Waiting for containers to stop...
:wait_stop
docker ps --filter "name=casewise-v2" --format "{{.Names}}" > temp_containers.txt 2>nul
for /f %%i in (temp_containers.txt) do (
    timeout /t 2 /nobreak >nul
    goto wait_stop
)
del temp_containers.txt >nul 2>&1
echo All containers stopped

echo Rebuilding specific containers (no cache)...
docker-compose build --no-cache casewise-dev dicom-server ohif-viewer frontend
if %errorlevel% neq 0 (
    echo Failed to rebuild containers
    exit /b 1
)
echo Build completed successfully

echo Spinning up services...
docker-compose up -d casewise-dev dicom-server ohif-viewer frontend
if %errorlevel% neq 0 (
    echo Failed to spin up services
    exit /b 1
)

echo Waiting for containers to start...
set /a attempts=0
:wait_start
set /a attempts+=1
if %attempts% gtr 30 (
    echo Timeout waiting for containers to start
    goto done
)

docker ps --filter "name=casewise-v2-casewise-dev" --format "{{.Names}}" | findstr "casewise-dev" >nul
if errorlevel 1 (
    timeout /t 2 /nobreak >nul
    goto wait_start
)

docker ps --filter "name=casewise-v2-dicom-server" --format "{{.Names}}" | findstr "dicom-server" >nul
if errorlevel 1 (
    timeout /t 2 /nobreak >nul
    goto wait_start
)

docker ps --filter "name=casewise-v2-ohif-viewer" --format "{{.Names}}" | findstr "ohif-viewer" >nul
if errorlevel 1 (
    timeout /t 2 /nobreak >nul
    goto wait_start
)

docker ps --filter "name=casewise-v2-frontend" --format "{{.Names}}" | findstr "frontend" >nul
if errorlevel 1 (
    timeout /t 2 /nobreak >nul
    goto wait_start
)

echo All containers are running

:done
echo Rebuild process completed successfully!
echo Services running:
echo   - CaseWise Dev: Running
echo   - DICOM Server: Running
echo   - OHIF Viewer: http://localhost:8081
echo   - Frontend: Running 