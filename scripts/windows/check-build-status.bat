@echo off
REM Diagnostic script to check build status

setlocal enabledelayedexpansion

echo =========================================
echo Build Status Check
echo =========================================
echo.

REM ===========================================
REM Backend Build Status
REM ===========================================
echo 1. Backend Build Status
echo -----------------------------------------
if exist "backend\dist\backend.exe" (
    echo [SUCCESS] backend\dist\backend.exe EXISTS
    dir /s backend\dist\backend.exe | findstr /C:"backend.exe"
) else (
    echo [ERROR] backend\dist\backend.exe NOT FOUND
)
echo.

REM ===========================================
REM Electron Resources Status
REM ===========================================
echo 2. Electron Resources Status
echo -----------------------------------------
if exist "electron\resources" (
    echo [SUCCESS] electron\resources\ exists
    echo Contents:
    dir /b electron\resources
    echo.
    
    if exist "electron\resources\backend.exe" (
        echo [SUCCESS] Backend is in resources
    ) else (
        echo [ERROR] Backend NOT in resources
    )
    
    if exist "electron\resources\frontend" (
        echo [SUCCESS] Frontend is in resources
    ) else (
        echo [ERROR] Frontend NOT in resources
    )
) else (
    echo [ERROR] electron\resources\ does NOT exist
)
echo.

REM ===========================================
REM Frontend Build Status
REM ===========================================
echo 3. Frontend Build Status
echo -----------------------------------------
if exist "frontend\build" (
    echo [SUCCESS] frontend\build\ exists
    if exist "frontend\build\index.html" (
        echo [SUCCESS] Frontend appears complete
    ) else (
        echo [WARNING] index.html not found
    )
) else (
    echo [ERROR] frontend\build\ NOT FOUND
)
echo.

REM ===========================================
REM Electron Build Status
REM ===========================================
echo 4. Electron Build Status
echo -----------------------------------------
if exist "electron\dist" (
    echo [SUCCESS] electron\dist\ exists
    echo Contents:
    dir /b electron\dist
) else (
    echo [ERROR] electron\dist\ does NOT exist
)
echo.

REM ===========================================
REM Dependencies Check
REM ===========================================
echo 5. Dependencies Check
echo -----------------------------------------

echo PyInstaller:
python -m PyInstaller --version >nul 2>&1
if !errorlevel! equ 0 (
    python -m PyInstaller --version
    echo [SUCCESS] PyInstaller installed
) else (
    echo [ERROR] PyInstaller NOT installed
)

echo.
echo pnpm:
pnpm --version >nul 2>&1
if !errorlevel! equ 0 (
    pnpm --version
    echo [SUCCESS] pnpm installed
) else (
    echo [WARNING] pnpm NOT installed
)

echo.
echo npm:
npm --version >nul 2>&1
if !errorlevel! equ 0 (
    npm --version
    echo [SUCCESS] npm installed
) else (
    echo [ERROR] npm NOT installed
)

echo.
echo Node.js:
node --version >nul 2>&1
if !errorlevel! equ 0 (
    node --version
    echo [SUCCESS] Node.js installed
) else (
    echo [ERROR] Node.js NOT installed
)

echo.
echo Python:
python --version >nul 2>&1
if !errorlevel! equ 0 (
    python --version
    echo [SUCCESS] Python installed
) else (
    echo [ERROR] Python NOT installed
)

echo.
echo =========================================
echo Diagnosis Complete
echo =========================================
echo.
echo If backend is missing from resources:
echo   Run: scripts\build-windows.bat
echo.
echo If only Electron build is missing:
echo   cd electron ^&^& npm run build:win
echo.
pause

