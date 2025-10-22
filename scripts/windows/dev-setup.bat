@echo off
REM Grammar Correction App - Development Setup Script
REM This script sets up the development environment for the Grammar Correction App

setlocal enabledelayedexpansion

echo.
echo ========================================
echo   Grammar Correction App Setup
echo ========================================
echo.

REM Check if we're in the right directory
if not exist "backend\main.py" (
    echo [ERROR] Please run this script from the project root directory
    exit /b 1
)

echo [INFO] Starting development environment setup...
echo.

REM ===========================================
REM Check Requirements
REM ===========================================
echo [INFO] Checking system requirements...

REM Check Python
where python >nul 2>&1
if !errorlevel! neq 0 (
    echo [ERROR] Python is not installed. Please install Python 3.9 or higher.
    exit /b 1
) else (
    echo [SUCCESS] Python is available
)

REM Check Node.js
where node >nul 2>&1
if !errorlevel! neq 0 (
    echo [ERROR] Node.js is not installed. Please install Node.js 18 or higher.
    exit /b 1
) else (
    echo [SUCCESS] Node.js is available
)

REM Check npm
where npm >nul 2>&1
if !errorlevel! neq 0 (
    echo [ERROR] npm is not installed. Please install Node.js first.
    exit /b 1
) else (
    echo [SUCCESS] npm is available
)

REM Check pnpm (optional but recommended)
where pnpm >nul 2>&1
if !errorlevel! neq 0 (
    echo [WARNING] pnpm is not installed. Installing pnpm...
    call npm install -g pnpm
    if !errorlevel! equ 0 (
        echo [SUCCESS] pnpm installed successfully
    ) else (
        echo [WARNING] Failed to install pnpm. Will use npm instead.
    )
) else (
    echo [SUCCESS] pnpm is available
)

REM Check Docker
where docker >nul 2>&1
if !errorlevel! neq 0 (
    echo [WARNING] Docker is not installed. Docker is optional but recommended for LanguageTool.
) else (
    echo [SUCCESS] Docker is available
)

echo.

REM ===========================================
REM Setup Environment Files
REM ===========================================
echo [INFO] Setting up environment files...

if not exist ".env" (
    copy env.example .env >nul
    echo [SUCCESS] Created .env file from env.example
) else (
    echo [WARNING] .env file already exists, skipping...
)

if not exist "backend\.env" (
    (
        echo LANGUAGETOOL_URL=http://localhost:8081
        echo MAX_FILE_SIZE=10485760
        echo PROCESSING_TIMEOUT=300
        echo CORS_ORIGINS=http://localhost:3000
        echo DEBUG=true
        echo LOG_LEVEL=INFO
    ) > backend\.env
    echo [SUCCESS] Created backend\.env file
) else (
    echo [WARNING] backend\.env already exists, skipping...
)

if not exist "frontend\.env" (
    echo REACT_APP_API_URL=http://localhost:8000 > frontend\.env
    echo [SUCCESS] Created frontend\.env file
) else (
    echo [WARNING] frontend\.env already exists, skipping...
)

echo.

REM ===========================================
REM Setup Backend
REM ===========================================
echo [INFO] Setting up backend environment...

cd backend

REM Create virtual environment
if not exist "venv" (
    echo [INFO] Creating Python virtual environment...
    python -m venv venv
    if !errorlevel! neq 0 (
        echo [ERROR] Failed to create virtual environment
        cd ..
        exit /b 1
    )
)

REM Activate virtual environment
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo [INFO] Upgrading pip...
python -m pip install --upgrade pip >nul 2>&1

REM Install dependencies
echo [INFO] Installing Python dependencies (this may take a few minutes)...
pip install -r requirements.txt
if !errorlevel! neq 0 (
    echo [ERROR] Failed to install Python dependencies
    cd ..
    exit /b 1
)

REM Create necessary directories
if not exist "temp_files" mkdir temp_files
if not exist "uploads" mkdir uploads

echo [SUCCESS] Backend environment setup completed
cd ..
echo.

REM ===========================================
REM Setup Frontend
REM ===========================================
echo [INFO] Setting up frontend environment...

cd frontend

REM Clean existing node_modules if they exist
if exist "node_modules" (
    echo [INFO] Cleaning existing node_modules...
    rmdir /s /q node_modules 2>nul
)

REM Install dependencies with pnpm or npm
echo [INFO] Installing Node.js dependencies (this may take a few minutes)...
where pnpm >nul 2>&1
if !errorlevel! equ 0 (
    echo [INFO] Using pnpm...
    pnpm install --no-strict-peer-dependencies
    if !errorlevel! neq 0 (
        echo [WARNING] pnpm install failed, trying with force flag...
        pnpm install --force --no-strict-peer-dependencies
    )
) else (
    echo [INFO] Using npm...
    npm install --legacy-peer-deps
)

if !errorlevel! neq 0 (
    echo [ERROR] Failed to install Node.js dependencies
    cd ..
    exit /b 1
)

echo [SUCCESS] Frontend environment setup completed
cd ..
echo.

REM ===========================================
REM Setup LanguageTool
REM ===========================================
echo [INFO] Checking LanguageTool...

curl -s http://localhost:8081/v2/languages >nul 2>&1
if !errorlevel! equ 0 (
    echo [SUCCESS] LanguageTool is already running on localhost:8081
) else (
    echo [WARNING] LanguageTool is not running. You can start it with:
    echo [WARNING]   docker run -d -p 8081:8081 silviof/docker-languagetool:latest
    echo [WARNING]   or use the docker-compose setup
)

echo.

REM ===========================================
REM Verify Setup
REM ===========================================
echo [INFO] Verifying setup...

REM Verify backend
cd backend
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    python -c "from services.grammar_checker import GrammarChecker; print('[SUCCESS] Backend grammar checker verified')" 2>nul
    if !errorlevel! neq 0 (
        echo [WARNING] Backend grammar checker verification failed
    )
) else (
    echo [WARNING] Backend virtual environment not found
)
cd ..

REM Verify frontend
cd frontend
if exist "node_modules" (
    if exist "package.json" (
        echo [SUCCESS] Frontend dependencies verified
    ) else (
        echo [WARNING] package.json not found
    )
) else (
    echo [WARNING] Frontend node_modules not found
)
cd ..

echo.

REM ===========================================
REM Final Summary
REM ===========================================
echo ========================================
echo   Setup Complete!
echo ========================================
echo.
echo [SUCCESS] Development environment setup completed!
echo.
echo Next steps:
echo   1. Start LanguageTool (optional):
echo      docker run -d -p 8081:8081 silviof/docker-languagetool:latest
echo.
echo   2. Start backend:
echo      scripts\start-backend.bat
echo.
echo   3. Start frontend:
echo      scripts\start-frontend.bat
echo.
echo   4. Or start both with:
echo      scripts\start-dev.bat
echo.
echo   5. Or use Docker Compose:
echo      docker-compose up --build
echo.
echo The application will be available at:
echo   - Frontend:          http://localhost:3000
echo   - Backend API:       http://localhost:8000
echo   - API Documentation: http://localhost:8000/docs
echo.
echo ========================================
echo.
pause

