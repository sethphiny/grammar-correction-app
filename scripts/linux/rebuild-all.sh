#!/bin/bash
# Complete rebuild script with verification at each step

set -e  # Exit on error

PROJECT_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"
cd "$PROJECT_ROOT"

echo "========================================="
echo "Complete Rebuild Script"
echo "========================================="
echo ""

# Step 1: Clean
echo "Step 1: Cleaning old builds..."
echo "-----------------------------------------"
rm -rf backend/build backend/dist
rm -rf electron/resources
rm -rf electron/dist
echo "✓ Clean complete"
echo ""

# Step 2: Build backend
echo "Step 2: Building Python backend..."
echo "-----------------------------------------"
cd backend
python3 -m PyInstaller --clean --noconfirm main.spec

# Verify backend was built
if [ ! -f "dist/backend" ]; then
    echo "❌ ERROR: Backend build failed!"
    echo "Check backend/dist/ for errors"
    exit 1
fi
echo "✓ Backend built: $(ls -lh dist/backend | awk '{print $5}')"
cd ..
echo ""

# Step 3: Copy backend to Electron resources
echo "Step 3: Copying backend to Electron..."
echo "-----------------------------------------"
mkdir -p electron/resources
cp backend/dist/backend electron/resources/backend
chmod +x electron/resources/backend

# Verify copy
if [ ! -f "electron/resources/backend" ]; then
    echo "❌ ERROR: Backend not copied!"
    exit 1
fi
echo "✓ Backend copied to: electron/resources/backend"
echo "  Size: $(ls -lh electron/resources/backend | awk '{print $5}')"
echo ""

# Step 4: Build frontend
echo "Step 4: Building React frontend..."
echo "-----------------------------------------"
cd frontend
pnpm run build
if [ ! -d "build" ]; then
    echo "❌ ERROR: Frontend build failed!"
    exit 1
fi
echo "✓ Frontend built"
cd ..
echo ""

# Step 5: Copy frontend to resources
echo "Step 5: Copying frontend to Electron..."
echo "-----------------------------------------"
cp -r frontend/build electron/resources/frontend
if [ ! -f "electron/resources/frontend/index.html" ]; then
    echo "❌ ERROR: Frontend not copied correctly!"
    exit 1
fi
echo "✓ Frontend copied"
echo ""

# Step 6: Verify resources
echo "Step 6: Verifying resources..."
echo "-----------------------------------------"
echo "Contents of electron/resources/:"
ls -lh electron/resources/
echo ""

# Step 7: Install Electron dependencies
echo "Step 7: Installing Electron dependencies..."
echo "-----------------------------------------"
cd electron
rm -rf node_modules package-lock.json
npm install
echo "✓ Dependencies installed"
cd ..
echo ""

# Step 8: Build Electron app
echo "Step 8: Building Electron application..."
echo "-----------------------------------------"
cd electron
npm run build:win
cd ..
echo ""

# Step 9: Show results
echo "========================================="
echo "✅ BUILD COMPLETE!"
echo "========================================="
echo ""
echo "Executable location:"
if [ -f "electron/dist/Grammar Correction App"*.exe ]; then
    ls -lh electron/dist/*.exe
elif [ -d "electron/dist/win-unpacked" ]; then
    echo "Unpacked version:"
    ls -lh electron/dist/win-unpacked/
else
    echo "Check electron/dist/ directory:"
    ls -l electron/dist/
fi
echo ""
echo "To run: cd electron/dist && ./<executable-name>"

