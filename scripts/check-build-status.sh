#!/bin/bash
# Diagnostic script to check build status

echo "========================================="
echo "Build Status Check"
echo "========================================="
echo ""

echo "1. Backend Build Status"
echo "-----------------------------------------"
if [ -f "backend/dist/backend" ]; then
    echo "✓ backend/dist/backend EXISTS"
    ls -lh backend/dist/backend
else
    echo "❌ backend/dist/backend NOT FOUND"
fi
echo ""

echo "2. Electron Resources Status"
echo "-----------------------------------------"
if [ -d "electron/resources" ]; then
    echo "✓ electron/resources/ exists"
    echo "Contents:"
    ls -lh electron/resources/
    echo ""
    if [ -f "electron/resources/backend" ]; then
        echo "✓ Backend is in resources"
    else
        echo "❌ Backend NOT in resources"
    fi
    if [ -d "electron/resources/frontend" ]; then
        echo "✓ Frontend is in resources"
    else
        echo "❌ Frontend NOT in resources"
    fi
else
    echo "❌ electron/resources/ does NOT exist"
fi
echo ""

echo "3. Frontend Build Status"
echo "-----------------------------------------"
if [ -d "frontend/build" ]; then
    echo "✓ frontend/build/ exists"
    if [ -f "frontend/build/index.html" ]; then
        echo "✓ Frontend appears complete"
    fi
else
    echo "❌ frontend/build/ NOT FOUND"
fi
echo ""

echo "4. Electron Build Status"
echo "-----------------------------------------"
if [ -d "electron/dist" ]; then
    echo "✓ electron/dist/ exists"
    echo "Contents:"
    ls -lh electron/dist/
else
    echo "❌ electron/dist/ does NOT exist"
fi
echo ""

echo "5. Dependencies Check"
echo "-----------------------------------------"
echo "PyInstaller:"
python3 -m PyInstaller --version 2>/dev/null && echo "✓ PyInstaller installed" || echo "❌ PyInstaller NOT installed"

echo "pnpm:"
pnpm --version 2>/dev/null && echo "✓ pnpm installed" || echo "❌ pnpm NOT installed"

echo "npm:"
npm --version 2>/dev/null && echo "✓ npm installed" || echo "❌ npm NOT installed"

echo ""
echo "========================================="
echo "Diagnosis Complete"
echo "========================================="
echo ""
echo "If backend is missing from resources:"
echo "  Run: ./scripts/rebuild-all.sh"
echo ""
echo "If only Electron build is missing:"
echo "  cd electron && npm run build:win"

