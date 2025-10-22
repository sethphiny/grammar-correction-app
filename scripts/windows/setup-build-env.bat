@echo off
REM Setup script for Windows build environment
REM Run this once before building for the first time

echo ========================================================================
echo Grammar Correction App - Build Environment Setup
echo ========================================================================
echo.

REM Get script directory
set SCRIPT_DIR=%~dp0
set PROJECT_ROOT=%SCRIPT_DIR%..
cd /d "%PROJECT_ROOT%"

echo This script will set up your build environment with all required dependencies.
echo.
echo Prerequisites:
echo   - Python 3.8 or higher
echo   - Node.js 18 or higher
echo   - pnpm (will be installed if missing)
echo.
pause

echo Step 1: Checking Python
echo ------------------------------------------------------------------------
python --version
if %ERRORLEVEL% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/
    exit /b 1
)
echo OK: Python is available
echo.

echo Step 2: Checking Node.js
echo ------------------------------------------------------------------------
node --version
if %ERRORLEVEL% neq 0 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js 18+ from https://nodejs.org/
    exit /b 1
)
echo OK: Node.js is available
echo.

echo Step 3: Installing/Checking pnpm
echo ------------------------------------------------------------------------
pnpm --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Installing pnpm...
    npm install -g pnpm
    if %ERRORLEVEL% neq 0 (
        echo ERROR: Failed to install pnpm
        exit /b 1
    )
)
pnpm --version
echo OK: pnpm is available
echo.

echo Step 4: Installing Python Dependencies
echo ------------------------------------------------------------------------
cd backend
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo ERROR: Failed to install Python dependencies
    exit /b 1
)
echo.
echo Installing Spacy model...
python -m spacy download en_core_web_sm
if %ERRORLEVEL% neq 0 (
    echo WARNING: Failed to download Spacy model
    echo You may need to download it manually: python -m spacy download en_core_web_sm
)
cd ..
echo OK: Python dependencies installed
echo.

echo Step 5: Installing Frontend Dependencies
echo ------------------------------------------------------------------------
cd frontend
pnpm install
if %ERRORLEVEL% neq 0 (
    echo ERROR: Failed to install frontend dependencies
    exit /b 1
)
cd ..
echo OK: Frontend dependencies installed
echo.

echo Step 6: Installing PyInstaller
echo ------------------------------------------------------------------------
python -m pip install pyinstaller
if %ERRORLEVEL% neq 0 (
    echo ERROR: Failed to install PyInstaller
    exit /b 1
)
echo OK: PyInstaller installed
echo.

echo Step 7: Creating necessary directories
echo ------------------------------------------------------------------------
if not exist "electron\resources" mkdir "electron\resources"
if not exist "electron\build" mkdir "electron\build"
echo OK: Directories created
echo.

echo ========================================================================
echo Setup Complete!
echo ========================================================================
echo.
echo Your build environment is now ready.
echo.
echo Next steps:
echo   1. Make sure you have an icon.png file in the electron folder
echo   2. Update electron/package.json with your GitHub repository info
echo   3. Run scripts\build-windows.bat to build the application
echo.
pause

