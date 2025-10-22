@echo off
REM Start Frontend Development Server
REM This script starts the React frontend development server

setlocal enabledelayedexpansion

echo.
echo ========================================
echo   Grammar Correction Frontend Server
echo ========================================
echo.

REM Check if we're in the right directory
if not exist "frontend\package.json" (
    echo [ERROR] Please run this script from the project root directory
    exit /b 1
)

echo [INFO] Starting Grammar Correction Frontend Server...
echo.

REM Check if node_modules exists
if not exist "frontend\node_modules" (
    echo [ERROR] Node modules not found
    echo [ERROR] Please run: cd frontend ^& npm install
    exit /b 1
)

REM Check if npm is available
where npm >nul 2>&1
if !errorlevel! neq 0 (
    echo [ERROR] npm is not installed. Please install Node.js first
    exit /b 1
)

REM Change to frontend directory
cd frontend

REM Check if backend is running
echo [INFO] Checking backend connection...
curl -s http://localhost:8000/health >nul 2>&1
if !errorlevel! equ 0 (
    echo [SUCCESS] Backend is running on localhost:8000
) else (
    echo [WARNING] Backend is not running. Please start it with: scripts\start-backend.bat
    echo [WARNING] Frontend will still start but API calls will fail.
)
echo.

echo [INFO] Starting React development server...
echo [INFO] Frontend will be available at: http://localhost:3000
echo [INFO] Press Ctrl+C to stop the server
echo.

REM Check if pnpm is available, otherwise use npm
where pnpm >nul 2>&1
if !errorlevel! equ 0 (
    echo [INFO] Using pnpm...
    pnpm start
) else (
    echo [INFO] Using npm...
    npm start
)

