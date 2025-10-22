@echo off
REM Start Development Environment
REM This script starts both backend and frontend servers concurrently

setlocal enabledelayedexpansion

echo.
echo ========================================
echo   Grammar Correction App - Development
echo ========================================
echo.

REM Check if we're in the right directory
if not exist "backend\main.py" (
    echo [ERROR] Please run this script from the project root directory
    exit /b 1
)
if not exist "frontend\package.json" (
    echo [ERROR] Please run this script from the project root directory
    exit /b 1
)

echo [INFO] Starting Grammar Correction App Development Environment...
echo.

REM Check if LanguageTool is running
echo [INFO] Checking LanguageTool connection...
curl -s http://localhost:8081/v2/languages >nul 2>&1
if !errorlevel! equ 0 (
    echo [SUCCESS] LanguageTool is running on localhost:8081
) else (
    echo [WARNING] LanguageTool is not running. Starting with Docker...
    docker run -d -p 8081:8081 --name languagetool silviof/docker-languagetool:latest >nul 2>&1
    timeout /t 5 /nobreak >nul
    curl -s http://localhost:8081/v2/languages >nul 2>&1
    if !errorlevel! equ 0 (
        echo [SUCCESS] LanguageTool started successfully
    ) else (
        echo [WARNING] LanguageTool failed to start. Grammar checking will use fallback methods.
    )
)
echo.

REM Start backend in new window
echo [INFO] Starting backend server...
start "Grammar Correction Backend" cmd /k "cd /d "%CD%" && call scripts\start-backend.bat"

REM Wait a moment for backend to start
echo [INFO] Waiting for backend to initialize...
timeout /t 5 /nobreak >nul

REM Check if backend started successfully
curl -s http://localhost:8000/health >nul 2>&1
if !errorlevel! equ 0 (
    echo [SUCCESS] Backend started successfully on http://localhost:8000
) else (
    echo [WARNING] Backend may not have started properly
    echo [WARNING] Check the backend window for details
)
echo.

REM Start frontend in new window
echo [INFO] Starting frontend server...
start "Grammar Correction Frontend" cmd /k "cd /d "%CD%" && call scripts\start-frontend.bat"

REM Wait a moment for frontend to start
echo [INFO] Waiting for frontend to initialize...
timeout /t 3 /nobreak >nul
echo.

echo ========================================
echo   Development Environment Started!
echo ========================================
echo.
echo Services running in separate windows:
echo   - Backend API:        http://localhost:8000
echo   - Frontend App:       http://localhost:3000
echo   - API Documentation:  http://localhost:8000/docs
echo.
echo To stop the servers:
echo   - Close the backend and frontend windows, or
echo   - Press Ctrl+C in each window
echo.
echo ========================================
echo.
pause

