@echo off
REM Test All Components
REM This script runs all tests for the Grammar Correction App

setlocal enabledelayedexpansion

echo.
echo ========================================
echo   Grammar Correction App - Tests
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

set "EXIT_CODE=0"

REM ===========================================
REM Backend Tests
REM ===========================================
echo [INFO] Running backend tests...
echo.

cd backend

if not exist "venv" (
    echo [ERROR] Virtual environment not found. Please run: scripts\dev-setup.bat first
    set "EXIT_CODE=1"
    goto frontend_tests
)

call venv\Scripts\activate.bat

REM Install test dependencies
pip install pytest pytest-asyncio pytest-cov >nul 2>&1

if exist "tests" (
    python -m pytest tests/ -v --cov=. --cov-report=term-missing
    if !errorlevel! neq 0 (
        echo [ERROR] Backend tests failed
        set "EXIT_CODE=1"
    ) else (
        echo [SUCCESS] Backend tests passed
    )
) else (
    echo [WARNING] No tests directory found in backend
    echo [INFO] Creating basic test structure...
    
    mkdir tests
    
    echo # Tests package > tests\__init__.py
    
    (
        echo import pytest
        echo from fastapi.testclient import TestClient
        echo from main import app
        echo.
        echo client = TestClient^(app^)
        echo.
        echo def test_health_check^(^):
        echo     response = client.get^("/health"^)
        echo     assert response.status_code == 200
        echo     assert response.json^(^)["status"] == "healthy"
        echo.
        echo def test_upload_invalid_file^(^):
        echo     response = client.post^("/upload", files={"file": ^("test.txt", b"test content", "text/plain"^)}^)
        echo     assert response.status_code == 400
    ) > tests\test_main.py
    
    python -m pytest tests/ -v
    if !errorlevel! neq 0 (
        set "EXIT_CODE=1"
    )
)

cd ..
echo.

REM ===========================================
REM Frontend Tests
REM ===========================================
:frontend_tests
echo [INFO] Running frontend tests...
echo.

cd frontend

if not exist "node_modules" (
    echo [ERROR] Node modules not found. Please run: scripts\dev-setup.bat first
    set "EXIT_CODE=1"
    goto linting
)

where pnpm >nul 2>&1
if !errorlevel! equ 0 (
    pnpm test --watchAll=false --coverage --passWithNoTests
) else (
    npm test -- --watchAll=false --coverage --passWithNoTests
)

if !errorlevel! neq 0 (
    echo [ERROR] Frontend tests failed
    set "EXIT_CODE=1"
) else (
    echo [SUCCESS] Frontend tests passed
)

cd ..
echo.

REM ===========================================
REM Code Quality Checks
REM ===========================================
:linting
echo [INFO] Running code quality checks...
echo.

REM Backend linting
echo [INFO] Checking backend code quality...
cd backend

if exist "venv" (
    call venv\Scripts\activate.bat
    
    pip install flake8 black isort >nul 2>&1
    
    echo [INFO] Running flake8...
    flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
    
    echo [INFO] Running black (check only)...
    black --check .
    
    echo [INFO] Running isort (check only)...
    isort --check-only .
)

cd ..
echo.

REM Frontend linting
echo [INFO] Checking frontend code quality...
cd frontend

if exist "node_modules" (
    where pnpm >nul 2>&1
    if !errorlevel! equ 0 (
        pnpm run lint
    ) else (
        npm run lint
    )
)

cd ..
echo.

REM ===========================================
REM Integration Tests
REM ===========================================
echo [INFO] Running integration tests...
echo.

REM Check if backend is running
curl -s http://localhost:8000/health >nul 2>&1
if !errorlevel! neq 0 (
    echo [WARNING] Backend is not running. Skipping integration tests.
    echo [WARNING] Start backend with: scripts\start-backend.bat
    goto summary
)

echo [INFO] Testing API endpoints...

REM Test health endpoint
curl -s http://localhost:8000/health | findstr /C:"healthy" >nul 2>&1
if !errorlevel! equ 0 (
    echo [SUCCESS] Health endpoint working
) else (
    echo [ERROR] Health endpoint failed
    set "EXIT_CODE=1"
)

REM Test API documentation
curl -s http://localhost:8000/docs >nul 2>&1
if !errorlevel! equ 0 (
    echo [SUCCESS] API documentation accessible
) else (
    echo [WARNING] API documentation not accessible
)

echo [SUCCESS] Integration tests completed
echo.

REM ===========================================
REM Summary
REM ===========================================
:summary
echo ========================================
if "%EXIT_CODE%"=="0" (
    echo   All Tests Passed!
    echo ========================================
) else (
    echo   Some Tests Failed
    echo ========================================
    echo.
    echo Check the output above for details.
)
echo.

exit /b %EXIT_CODE%

