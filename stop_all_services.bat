@echo off
TITLE LUNARIS-X (SIH26166) - Stop All Services
COLOR 0C

echo ===============================================================================
echo   LUNARIS-X (SIH26166) - Stopping All Multi-Tier Services...
echo ===============================================================================
echo.

echo Freeing Port 8000 (Python FastAPI ML Service)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8000" ^| findstr "LISTENING"') do (
    if "%%a" neq "0" (
        taskkill /F /PID %%a >nul 2>&1
    )
)

echo Freeing Port 8080 (Spring Boot Backend)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8080" ^| findstr "LISTENING"') do (
    if "%%a" neq "0" (
        taskkill /F /PID %%a >nul 2>&1
    )
)

echo Freeing Port 3000 (React Frontend)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":3000" ^| findstr "LISTENING"') do (
    if "%%a" neq "0" (
        taskkill /F /PID %%a >nul 2>&1
    )
)

echo.
echo ===============================================================================
echo   All LUNARIS-X (SIH26166) services have been terminated!
echo ===============================================================================
echo.
pause
