@echo off
title Bank App - Smart Appointment System
color 0A

echo ============================================
echo   AI-Based Smart Bank Appointment System
echo ============================================
echo.

:: Kill any previous instances on ports 5000 and 5173
echo [1/4] Cleaning up old processes...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":5000 " ^| findstr "LISTENING" 2^>nul') do (
    taskkill /F /PID %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":5173 " ^| findstr "LISTENING" 2^>nul') do (
    taskkill /F /PID %%a >nul 2>&1
)
echo    Done.
echo.

:: Navigate to project root
cd /d "%~dp0"

:: Check if venv exists
if not exist "venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found!
    echo    Run: python -m venv venv
    echo    Then: venv\Scripts\pip install flask flask-cors flask-sqlalchemy pandas joblib scikit-learn
    pause
    exit /b 1
)

:: Check if node_modules exists
if not exist "frontend\node_modules" (
    echo [WARNING] Node modules not found. Installing...
    cd frontend
    call npm install
    cd ..
    echo    Done.
    echo.
)

:: Start Backend
echo [2/4] Starting Backend Server (Flask on port 5000)...
start "Bank Backend" cmd /k "cd /d "%~dp0backend" && "%~dp0venv\Scripts\python.exe" app.py"
echo    Backend starting...
echo.

:: Wait a moment for backend to initialize
timeout /t 3 /nobreak >nul

:: Start Frontend
echo [3/4] Starting Frontend Server (Vite on port 5173)...
start "Bank Frontend" cmd /k "cd /d "%~dp0frontend" && npm run dev"
echo    Frontend starting...
echo.

:: Wait for frontend to be ready
timeout /t 5 /nobreak >nul

:: Open browser
echo [4/4] Opening browser...
start http://localhost:5173/
echo.

echo ============================================
echo   All services started successfully!
echo ============================================
echo.
echo   Customer Portal:    http://localhost:5173/
echo   Employee Dashboard: http://localhost:5173/employee
echo   Analytics:          http://localhost:5173/analytics
echo   Backend API:        http://localhost:5000/api
echo.
echo   To stop: Close the Backend and Frontend
echo   terminal windows, or press Ctrl+C in each.
echo ============================================
echo.
pause
