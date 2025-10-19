#!/bin/bash
# Build script for Windows Desktop Application
# This script builds the complete Windows executable

set -e  # Exit on error

echo "========================================================================"
echo "Grammar Correction App - Windows Build Script"
echo "========================================================================"
echo ""

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$SCRIPT_DIR/.."
cd "$PROJECT_ROOT"

echo "Step 1: Installing PyInstaller (if needed)"
echo "------------------------------------------------------------------------"
python3 -m pip install --quiet pyinstaller
echo "✓ PyInstaller is ready"
echo ""

echo "Step 2: Building Python Backend"
echo "------------------------------------------------------------------------"
python3 scripts/build-backend.py
echo "✓ Backend built successfully"
echo ""

echo "Step 3: Building React Frontend"
echo "------------------------------------------------------------------------"
cd frontend
pnpm run build
cd ..
echo "✓ Frontend built successfully"
echo ""

echo "Step 4: Copying Frontend Build to Electron Resources"
echo "------------------------------------------------------------------------"
mkdir -p electron/resources
rm -rf electron/resources/frontend
cp -r frontend/build electron/resources/frontend
echo "✓ Frontend copied to Electron resources"
echo ""

echo "Step 5: Installing Electron Dependencies"
echo "------------------------------------------------------------------------"
cd electron
npm install
cd ..
echo "✓ Electron dependencies installed"
echo ""

echo "Step 6: Building Electron Application"
echo "------------------------------------------------------------------------"
cd electron
npm run build:win
cd ..
echo "✓ Electron application built successfully"
echo ""

echo "========================================================================"
echo "Build Completed Successfully!"
echo "========================================================================"
echo ""
echo "Output location: electron/dist/"
echo "Executable: Grammar Correction App-*-portable.exe"
echo ""
echo "You can now run the portable executable from the dist folder."
echo ""

