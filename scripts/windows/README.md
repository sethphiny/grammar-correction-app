# Windows Scripts

This directory contains Windows batch scripts (.bat) for the Grammar Correction App.

> **💡 Tip:** If you have Git Bash installed, consider using the `scripts/linux/*.sh` scripts instead for better compatibility! See [../GITBASH_WINDOWS.md](../GITBASH_WINDOWS.md) for details.

## Available Scripts

### Development

- **`dev-setup.bat`** - Initial development environment setup
- **`start-backend.bat`** - Start FastAPI backend server
- **`start-frontend.bat`** - Start React frontend server
- **`start-dev.bat`** - Start both backend and frontend

### Testing

- **`test-all.bat`** - Run all tests and code quality checks

### Building

- **`build-windows.bat`** - Build Windows desktop application
- **`setup-build-env.bat`** - Setup build environment
- **`check-build-status.bat`** - Check build artifact status

## Quick Start

```cmd
REM From project root:

REM 1. Initial setup
scripts\windows\dev-setup.bat

REM 2. Start development servers
scripts\windows\start-dev.bat

REM 3. Run tests
scripts\windows\test-all.bat

REM 4. Build desktop app
scripts\windows\build-windows.bat
```

## Requirements

**Essential:**
- Windows 10 (21H1 or later) or Windows 11
- Python 3.9+ (3.11 recommended for best compatibility)
- Node.js 18+
- npm or pnpm
- **Microsoft C++ Build Tools** (required for spaCy)
  - Download: https://visualstudio.microsoft.com/visual-cpp-build-tools/
  - Select "Desktop development with C++" workload
  - ~7 GB disk space

**Optional:**
- Docker (for LanguageTool)

### Important: Install Build Tools First!

Before running `dev-setup.bat`, install Microsoft C++ Build Tools to avoid installation errors.

**Quick Install:**
1. Download: https://visualstudio.microsoft.com/visual-cpp-build-tools/
2. Run installer
3. Select "Desktop development with C++"
4. Install

**Having issues?** See [docs/WINDOWS_SETUP_TROUBLESHOOTING.md](../../docs/WINDOWS_SETUP_TROUBLESHOOTING.md)

## Notes

- All scripts should be run from the project root directory
- Virtual environment will be created automatically by dev-setup.bat
- Docker is optional but recommended for LanguageTool

## Documentation

See the main [scripts/README.md](../README.md) for detailed documentation.

