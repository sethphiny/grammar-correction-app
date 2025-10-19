# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added - Windows Desktop Executable (2025-10-19)

#### Electron Desktop Framework
- Created Electron main process (`electron/main.js`) with:
  - Backend process management and health checking
  - Window management with system tray integration
  - Auto-update functionality via electron-updater
  - Graceful backend process cleanup
  - Development and production mode support
  
- Created preload script (`electron/preload.js`) for:
  - Secure IPC communication
  - Context isolation
  - Safe API exposure to renderer

- Created Electron package configuration (`electron/package.json`) with:
  - electron-builder configuration
  - Portable Windows executable target
  - Auto-update GitHub integration
  - Build scripts for development and production

#### Backend Bundling
- Created PyInstaller spec file (`backend/main.spec`) with:
  - Hidden imports for all dependencies
  - Data file collection (spacy models, language tool)
  - Size optimization with excludes
  - One-file executable configuration

- Created backend build script (`scripts/build-backend.py`) with:
  - Dependency checking
  - Automated PyInstaller build
  - Error handling and verification
  - Automatic copy to Electron resources

#### Frontend Integration
- Modified `frontend/src/services/api.ts`:
  - Added Electron environment detection
  - Dynamic backend URL via IPC
  - WebSocket URL adjustment for Electron
  - Backward compatibility with web version

- Created `frontend/src/utils/electron.ts`:
  - Electron API type definitions
  - Helper functions for Electron features
  - Update status handlers
  - Version information access

#### Build System
- Created Windows build script (`scripts/build-windows.bat`)
- Created Unix/Linux build script (`scripts/build-windows.sh`)
- Created setup scripts:
  - `scripts/setup-build-env.bat` (Windows)
  - `scripts/setup-build-env.sh` (Unix/Linux)
- Full automated build pipeline:
  1. Backend bundling with PyInstaller
  2. Frontend React build
  3. Resource copying
  4. Electron packaging

#### Documentation
- Created `docs/BUILDING_WINDOWS_EXECUTABLE.md`:
  - Complete build instructions
  - Configuration guide
  - Troubleshooting section
  - Performance optimization tips

- Created `docs/TESTING_EXECUTABLE.md`:
  - Comprehensive test procedures
  - 13 functional test suites
  - Performance benchmarks
  - Stress test scenarios

- Created `docs/WINDOWS_DESKTOP_README.md`:
  - User documentation
  - Quick start guide
  - Configuration options
  - Troubleshooting for end users

- Created `docs/QUICK_START_GUIDE.md`:
  - 5-minute quick start for users
  - 4-step build guide for developers

- Created `electron/README.md`:
  - Electron-specific documentation
  - Development workflow
  - Configuration details

- Created `WINDOWS_DESKTOP_IMPLEMENTATION.md`:
  - Complete implementation overview
  - Architecture documentation
  - File structure guide

#### Configuration
- Created `electron/.env.example` for desktop app settings
- Updated `.gitignore` patterns for build artifacts

### Features
- Single portable Windows executable (~150-300 MB)
- No installation required
- Bundled Python runtime and all dependencies
- System tray integration with minimize
- Auto-update via GitHub releases
- Real-time backend health checking
- Graceful error handling and cleanup
- Development mode with hot reload
- Production mode with optimizations

### Technical Details
- Electron 28.x for desktop framework
- PyInstaller 6.x for Python bundling
- electron-builder 24.x for packaging
- electron-updater 6.x for auto-updates
- Context isolation and security hardening
- IPC-based communication
- One-file executable mode
- UPX compression for size optimization

### Compatibility
- Windows 10 (21H1 or later)
- Windows 11
- Windows Server 2019/2022
- x64 architecture

---

## Previous Entries

[Previous changelog entries remain here...]

## Fixed
- Fixed psutil import error in dashboard by adding proper error handling - now shows "N/A" for memory if psutil fails
- Fixed pandas FutureWarning messages by updating DataFrame concatenation to handle empty DataFrames properly
- Fixed TypeORM migration generation command by updating CLI configuration to use ts-node with proper TypeScript support
- Removed Vite proxy configuration from vite.config.ts - all frontend API calls now use absolute URLs

## Notes
- Windows desktop executable implementation is complete and ready for building
- Build requires Python 3.8+, Node.js 18+, and pnpm
- First build may take 10-20 minutes; subsequent builds 3-5 minutes
- Application icon (icon.png) must be provided by user
- Code signing certificate recommended for production releases
