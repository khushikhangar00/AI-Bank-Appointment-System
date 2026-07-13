@echo off
title Bank App - Shutdown
color 0C

echo ============================================
echo   Stopping Bank App Services...
echo ============================================
echo.

:: Kill processes on port 5000 (Backend)
echo Stopping Backend (port 5000)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":5000 " ^| findstr "LISTENING" 2^>nul') do (
    taskkill /F /PID %%a >nul 2>&1
)
echo    Done.

:: Kill processes on port 5173 (Frontend)
echo Stopping Frontend (port 5173)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":5173 " ^| findstr "LISTENING" 2^>nul') do (
    taskkill /F /PID %%a >nul 2>&1
)
echo    Done.

echo.
echo ============================================
echo   All services stopped.
echo ============================================
pause
