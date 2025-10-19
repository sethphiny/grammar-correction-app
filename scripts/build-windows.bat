@echo off
REM Build script for Windows Desktop Application
REM This script builds the complete Windows executable

echo ========================================================================
echo Grammar Correction App - Windows Build Script
echo ========================================================================
echo.

REM Set error handling
setlocal enabledelayedexpansion

REM Get script directory
set SCRIPT_DIR=%~dp0
set PROJECT_ROOT=%SCRIPT_DIR%..
cd /d "%PROJECT_ROOT%"

echo Step 1: Installing PyInstaller (if needed)
echo ------------------------------------------------------------------------
python -m pip install --quiet pyinstaller
if %ERRORLEVEL% neq 0 (
    echo ERROR: Failed to install PyInstaller
    exit /b 1
)
echo OK: PyInstaller is ready
echo.

echo Step 2: Building Python Backend
echo ------------------------------------------------------------------------
python scripts\build-backend.py
if %ERRORLEVEL% neq 0 (
    echo ERROR: Backend build failed
    exit /b 1
)
echo OK: Backend built successfully
echo.

echo Step 3: Building React Frontend
echo ------------------------------------------------------------------------
cd frontend
call pnpm run build
if %ERRORLEVEL% neq 0 (
    echo ERROR: Frontend build failed
    exit /b 1
)
cd ..
echo OK: Frontend built successfully
echo.

echo Step 4: Copying Frontend Build to Electron Resources
echo ------------------------------------------------------------------------
if not exist "electron\resources" mkdir "electron\resources"
if exist "electron\resources\frontend" rmdir /s /q "electron\resources\frontend"
xcopy /E /I /Y "frontend\build" "electron\resources\frontend"
if %ERRORLEVEL% neq 0 (
    echo ERROR: Failed to copy frontend build
    exit /b 1
)
echo OK: Frontend copied to Electron resources
echo.

echo Step 5: Installing Electron Dependencies
echo ------------------------------------------------------------------------
cd electron
call npm install
if %ERRORLEVEL% neq 0 (
    echo ERROR: Failed to install Electron dependencies
    exit /b 1
)
cd ..
echo OK: Electron dependencies installed
echo.

echo Step 6: Building Electron Application
echo ------------------------------------------------------------------------
cd electron
call npm run build:win
if %ERRORLEVEL% neq 0 (
    echo ERROR: Electron build failed
    exit /b 1
)
cd ..
echo OK: Electron application built successfully
echo.

echo ========================================================================
echo Build Completed Successfully!
echo ========================================================================
echo.
echo Output location: electron\dist\
echo Executable: Grammar Correction App-*-portable.exe
echo.
echo You can now run the portable executable from the dist folder.
echo.
pause

