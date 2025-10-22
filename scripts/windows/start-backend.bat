@echo off
REM Start Backend Development Server
REM This script starts the FastAPI backend server in development mode

setlocal enabledelayedexpansion

echo.
echo ========================================
echo   Grammar Correction Backend Server
echo ========================================
echo.

REM Check if we're in the right directory
if not exist "backend\main.py" (
    echo [ERROR] Please run this script from the project root directory
    exit /b 1
)

echo [INFO] Starting Grammar Correction Backend Server...
echo.

REM Check if virtual environment exists
if not exist "backend\venv" (
    echo [ERROR] Virtual environment not found
    echo [ERROR] Please run: scripts\dev-setup.bat first
    exit /b 1
)

REM Activate virtual environment
echo [INFO] Activating virtual environment...
call backend\venv\Scripts\activate.bat

REM Check if LanguageTool is running (optional)
echo [INFO] Checking LanguageTool connection...
curl -s http://localhost:8081/v2/languages >nul 2>&1
if !errorlevel! equ 0 (
    echo [SUCCESS] LanguageTool is running on localhost:8081
) else (
    echo [WARNING] LanguageTool is not running. Grammar checking will use fallback methods.
    echo [WARNING] To start LanguageTool: docker run -d -p 8081:8081 silviof/docker-languagetool:latest
)
echo.

REM Change to backend directory
cd backend

REM Set environment variables
set PYTHONPATH=%CD%
set PYTHONUNBUFFERED=1

echo [INFO] Starting FastAPI server with uvicorn...
echo [INFO] Backend will be available at: http://localhost:8000
echo [INFO] API documentation at: http://localhost:8000/docs
echo [INFO] Press Ctrl+C to stop the server
echo.

REM Start the server
uvicorn main:app --reload --host 0.0.0.0 --port 8000

