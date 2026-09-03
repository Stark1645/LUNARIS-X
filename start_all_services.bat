@echo off
TITLE SIH 2026 (SIH26166) - Multi-Tier Service Launcher
COLOR 0B

echo ===============================================================================
echo   SIH 2026 (SIH26166) - Lunar Image Registration Platform
echo   Initializing Multi-Tier Distributed Services...
echo ===============================================================================
echo.

:: Get Project Root Directory
set "ROOT_DIR=%~dp0"
cd /d "%ROOT_DIR%"

echo [Step 1/4] Checking and freeing ports 8000, 8080, and 3000...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8000" ^| findstr "LISTENING"') do (
    if "%%a" neq "0" (
        echo   - Freeing Port 8000 PID %%a
        taskkill /F /PID %%a >nul 2>&1
    )
)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8080" ^| findstr "LISTENING"') do (
    if "%%a" neq "0" (
        echo   - Freeing Port 8080 PID %%a
        taskkill /F /PID %%a >nul 2>&1
    )
)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":3000" ^| findstr "LISTENING"') do (
    if "%%a" neq "0" (
        echo   - Freeing Port 3000 PID %%a
        taskkill /F /PID %%a >nul 2>&1
    )
)

:: Wait 2 seconds for sockets to release
timeout /t 2 /nobreak >nul

echo.
echo [Step 2/4] Starting Python 3.13 FastAPI ML Engine on Port 8000...
start "SIH26166 - Python ML Service [Port 8000]" cmd /k "cd /d %ROOT_DIR% && py -3.13 -m uvicorn src.api.app:app --host 0.0.0.0 --port 8000"

echo [Step 3/4] Starting Java 21 Spring Boot 3 Backend on Port 8080...
start "SIH26166 - Spring Boot Backend [Port 8080]" cmd /k "cd /d %ROOT_DIR%backend && mvn spring-boot:run"

echo [Step 4/4] Starting React 18+ Vite Frontend on Port 3000...
start "SIH26166 - React Frontend [Port 3000]" cmd /k "cd /d %ROOT_DIR%frontend && npm.cmd run dev"

echo.
echo ===============================================================================
echo   Waiting for backend services to become healthy before opening browser...
echo ===============================================================================

:: Smart wait loop: wait until services are healthy before opening browser
py -3.13 -u "%ROOT_DIR%scripts\wait_for_services.py"

echo.
echo ===============================================================================
echo   Platform is Ready!
echo.
echo   - React Frontend:    http://localhost:3000
echo   - Spring Boot API:   http://localhost:8080/api/v1/health
echo   - Swagger API Docs:  http://localhost:8080/swagger-ui.html
echo   - Python ML Service: http://localhost:8000/docs
echo ===============================================================================

start http://localhost:3000

echo.
echo Press any key to close this launcher window (services will continue running).
pause >nul
