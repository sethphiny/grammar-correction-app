#!/bin/bash
# Setup script for build environment
# Run this once before building for the first time

set -e  # Exit on error

echo "========================================================================"
echo "Grammar Correction App - Build Environment Setup"
echo "========================================================================"
echo ""

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$SCRIPT_DIR/.."
cd "$PROJECT_ROOT"

echo "This script will set up your build environment with all required dependencies."
echo ""
echo "Prerequisites:"
echo "  - Python 3.8 or higher"
echo "  - Node.js 18 or higher"
echo "  - pnpm (will be installed if missing)"
echo ""
read -p "Press Enter to continue..."

echo ""
echo "Step 1: Checking Python"
echo "------------------------------------------------------------------------"
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.8+ from https://www.python.org/"
    exit 1
fi
python3 --version
echo "✓ Python is available"
echo ""

echo "Step 2: Checking Node.js"
echo "------------------------------------------------------------------------"
if ! command -v node &> /dev/null; then
    echo "ERROR: Node.js is not installed or not in PATH"
    echo "Please install Node.js 18+ from https://nodejs.org/"
    exit 1
fi
node --version
echo "✓ Node.js is available"
echo ""

echo "Step 3: Installing/Checking pnpm"
echo "------------------------------------------------------------------------"
if ! command -v pnpm &> /dev/null; then
    echo "Installing pnpm..."
    npm install -g pnpm
fi
pnpm --version
echo "✓ pnpm is available"
echo ""

echo "Step 4: Installing Python Dependencies"
echo "------------------------------------------------------------------------"
cd backend
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
echo ""
echo "Installing Spacy model..."
python3 -m spacy download en_core_web_sm || echo "WARNING: Failed to download Spacy model. You may need to run: python3 -m spacy download en_core_web_sm"
cd ..
echo "✓ Python dependencies installed"
echo ""

echo "Step 5: Installing Frontend Dependencies"
echo "------------------------------------------------------------------------"
cd frontend
pnpm install
cd ..
echo "✓ Frontend dependencies installed"
echo ""

echo "Step 6: Installing PyInstaller"
echo "------------------------------------------------------------------------"
python3 -m pip install pyinstaller
echo "✓ PyInstaller installed"
echo ""

echo "Step 7: Creating necessary directories"
echo "------------------------------------------------------------------------"
mkdir -p electron/resources
mkdir -p electron/build
echo "✓ Directories created"
echo ""

echo "========================================================================"
echo "Setup Complete!"
echo "========================================================================"
echo ""
echo "Your build environment is now ready."
echo ""
echo "Next steps:"
echo "  1. Make sure you have an icon.png file in the electron folder"
echo "  2. Update electron/package.json with your GitHub repository info"
echo "  3. Run scripts/build-windows.sh to build the application"
echo ""

