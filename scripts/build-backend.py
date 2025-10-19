#!/usr/bin/env python3
"""
Build script for creating a standalone backend executable using PyInstaller
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

# Get project root directory
PROJECT_ROOT = Path(__file__).parent.parent
BACKEND_DIR = PROJECT_ROOT / 'backend'
DIST_DIR = PROJECT_ROOT / 'dist' / 'backend'
SPEC_FILE = BACKEND_DIR / 'main.spec'
ELECTRON_RESOURCES = PROJECT_ROOT / 'electron' / 'resources'

def check_pyinstaller():
    """Check if PyInstaller is installed"""
    try:
        import PyInstaller
        print(f"✓ PyInstaller {PyInstaller.__version__} is installed")
        return True
    except ImportError:
        print("✗ PyInstaller is not installed")
        print("  Install it with: pip install pyinstaller")
        return False

def check_dependencies():
    """Check if all required dependencies are installed"""
    print("\nChecking dependencies...")
    
    # Map package names to their import names if different
    required_packages = {
        'fastapi': 'fastapi',
        'uvicorn': 'uvicorn',
        'language_tool_python': 'language_tool_python',
        'spacy': 'spacy',
        'openai': 'openai',
        'reportlab': 'reportlab',
        'python-docx': 'docx',  # Package name vs import name
        'docx2txt': 'docx2txt'
    }
    
    missing = []
    for package_name, import_name in required_packages.items():
        try:
            __import__(import_name)
            print(f"  ✓ {package_name}")
        except ImportError:
            print(f"  ✗ {package_name}")
            missing.append(package_name)
    
    if missing:
        print(f"\n✗ Missing packages: {', '.join(missing)}")
        print("  Install them with: pip install -r backend/requirements.txt")
        return False
    
    # Check for spacy model
    try:
        import en_core_web_sm
        print("  ✓ en_core_web_sm (spacy model)")
    except ImportError:
        print("  ✗ en_core_web_sm (spacy model)")
        print("  Download it with: python -m spacy download en_core_web_sm")
        return False
    
    return True

def clean_build():
    """Clean previous build artifacts"""
    print("\nCleaning previous builds...")
    
    dirs_to_clean = [
        BACKEND_DIR / 'build',
        BACKEND_DIR / 'dist',
        DIST_DIR,
    ]
    
    for dir_path in dirs_to_clean:
        if dir_path.exists():
            print(f"  Removing {dir_path}")
            shutil.rmtree(dir_path)
    
    print("✓ Clean completed")

def build_backend():
    """Build the backend executable using PyInstaller"""
    print("\nBuilding backend executable...")
    print(f"  Spec file: {SPEC_FILE}")
    print(f"  Output directory: {DIST_DIR}")
    
    # Change to backend directory
    os.chdir(BACKEND_DIR)
    
    # Run PyInstaller
    cmd = [
        sys.executable,
        '-m', 'PyInstaller',
        '--clean',
        '--noconfirm',
        str(SPEC_FILE)
    ]
    
    print(f"\n  Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=False)
    
    if result.returncode != 0:
        print("\n✗ Build failed!")
        return False
    
    print("\n✓ Build completed successfully")
    return True

def copy_to_electron():
    """Copy the built executable to Electron resources directory"""
    print("\nCopying executable to Electron resources...")
    
    # Create resources directory if it doesn't exist
    ELECTRON_RESOURCES.mkdir(parents=True, exist_ok=True)
    
    # Find the executable
    backend_exe = BACKEND_DIR / 'dist' / 'backend.exe'
    
    if not backend_exe.exists():
        # Try without .exe extension (for non-Windows builds during development)
        backend_exe = BACKEND_DIR / 'dist' / 'backend'
    
    if not backend_exe.exists():
        print(f"✗ Executable not found at {backend_exe}")
        return False
    
    # Copy to Electron resources
    dest = ELECTRON_RESOURCES / backend_exe.name
    shutil.copy2(backend_exe, dest)
    
    print(f"  ✓ Copied to {dest}")
    print(f"  Size: {dest.stat().st_size / (1024*1024):.1f} MB")
    
    return True

def main():
    """Main build process"""
    print("=" * 70)
    print("Grammar Correction Backend Build Script")
    print("=" * 70)
    
    # Check PyInstaller
    if not check_pyinstaller():
        sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Clean previous builds
    clean_build()
    
    # Build backend
    if not build_backend():
        sys.exit(1)
    
    # Copy to Electron resources
    if not copy_to_electron():
        sys.exit(1)
    
    print("\n" + "=" * 70)
    print("✓ Backend build completed successfully!")
    print("=" * 70)
    print(f"\nExecutable location: {ELECTRON_RESOURCES / 'backend.exe'}")
    print("\nNext steps:")
    print("  1. Build the frontend: cd frontend && pnpm run build")
    print("  2. Copy frontend build to electron/resources/frontend")
    print("  3. Build Electron app: cd electron && npm run build:win")

if __name__ == '__main__':
    main()

