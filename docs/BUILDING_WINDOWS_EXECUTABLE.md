# Building Windows Desktop Executable

This guide explains how to build a standalone Windows executable for the Grammar Correction App.

## Overview

The build process creates a single portable `.exe` file that includes:
- Python FastAPI backend (bundled with PyInstaller)
- React frontend (built and embedded)
- Electron wrapper for desktop functionality
- Auto-update capability via GitHub releases

## Prerequisites

Before building, ensure you have:

1. **Python 3.8+** - [Download](https://www.python.org/downloads/)
2. **Node.js 18+** - [Download](https://nodejs.org/)
3. **pnpm** - Package manager for Node.js
4. **Windows OS** - Required for building Windows executables

## Initial Setup

Run the setup script once before your first build:

### Windows
```bash
scripts\setup-build-env.bat
```

### macOS/Linux (for cross-platform development)
```bash
chmod +x scripts/setup-build-env.sh
./scripts/setup-build-env.sh
```

This script will:
- Check for required tools (Python, Node.js)
- Install pnpm if needed
- Install all Python dependencies
- Download Spacy language model
- Install frontend dependencies
- Install PyInstaller
- Create necessary directories

## Building the Application

### Full Build

To build the complete application, run:

#### Windows
```bash
scripts\build-windows.bat
```

#### macOS/Linux (requires Wine for Windows builds)
```bash
chmod +x scripts/build-windows.sh
./scripts/build-windows.sh
```

The build process includes:
1. Building Python backend with PyInstaller
2. Building React frontend
3. Copying frontend to Electron resources
4. Installing Electron dependencies
5. Building Electron app with electron-builder

### Build Output

The final executable will be located at:
```
electron/dist/Grammar Correction App-1.0.0-portable.exe
```

File size: Approximately 150-300 MB (includes Python runtime and all dependencies)

## Partial Builds

You can also run individual build steps:

### Backend Only
```bash
python scripts/build-backend.py
```
Output: `electron/resources/backend.exe`

### Frontend Only
```bash
cd frontend
pnpm run build
```
Output: `frontend/build/`

### Electron Only (after backend and frontend are built)
```bash
cd electron
npm install
npm run build:win
```

## Configuration

### Application Icon

Place a `icon.png` file (512x512 or larger) in the `electron/` directory. This will be used for:
- Application window icon
- System tray icon
- Installer icon

### Auto-Update Configuration

Edit `electron/package.json` and update the publish section:

```json
{
  "build": {
    "publish": {
      "provider": "github",
      "owner": "your-github-username",
      "repo": "grammar-correction-app",
      "releaseType": "release"
    }
  }
}
```

### Environment Variables

Create a `.env` file in the project root for configuration:

```env
# OpenAI API Key (if using LLM features)
OPENAI_API_KEY=your-api-key-here

# Maximum file size (in bytes, default 10MB)
MAX_FILE_SIZE=10485760

# CORS origins (comma-separated)
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
```

The `.env` file will be bundled with the backend executable.

## Troubleshooting

### PyInstaller Issues

**Problem**: PyInstaller fails to import modules
**Solution**: Add missing modules to `hiddenimports` in `backend/main.spec`

**Problem**: Backend executable is too large
**Solution**: Add packages to `excludes` in `backend/main.spec`

### Electron Builder Issues

**Problem**: Electron build fails with "cannot find module"
**Solution**: Ensure all dependencies are in `electron/package.json` dependencies, not devDependencies

**Problem**: Backend not found in packaged app
**Solution**: Verify `backend.exe` exists in `electron/resources/` before building

### Frontend Issues

**Problem**: Frontend can't connect to backend
**Solution**: Check that the Electron API is properly exposed in `preload.js`

### Build Performance

- **First build**: 10-20 minutes (downloads and caches dependencies)
- **Subsequent builds**: 3-5 minutes (uses cached dependencies)
- **Backend only**: 2-3 minutes
- **Frontend only**: 1-2 minutes

## Build Artifacts

After a successful build, you'll have:

```
electron/
  dist/
    Grammar Correction App-1.0.0-portable.exe  # Portable executable
    builder-effective-config.yaml              # Build configuration used
    win-unpacked/                              # Unpacked files (for debugging)
```

## Distribution

The portable executable can be distributed as-is:
- No installation required
- Runs from any location
- Creates app data in user's AppData folder
- Automatically checks for updates

### Creating a Release

1. Build the application
2. Test the executable thoroughly
3. Create a GitHub release with the executable as an asset
4. Users will receive automatic update notifications

## Development Mode

To run the app in development mode (without building):

1. Start backend:
```bash
cd backend
python3 main.py
```

2. Start frontend:
```bash
cd frontend
pnpm start
```

3. Start Electron (optional):
```bash
cd electron
npm run dev
```

In development mode:
- Frontend runs on `http://localhost:3000`
- Backend runs on `http://localhost:8000`
- Electron loads from the dev server
- Hot reload is enabled

## Advanced Topics

### Custom PyInstaller Hooks

Create custom hooks in `backend/hooks/` if you need special handling for imports.

### Code Signing (Windows)

For production releases, sign the executable:

1. Obtain a code signing certificate
2. Add to `electron/package.json`:
```json
{
  "win": {
    "certificateFile": "path/to/cert.pfx",
    "certificatePassword": "password"
  }
}
```

### Installer Version

To create an installer instead of portable executable:

```bash
cd electron
npm run build:win:installer
```

This creates an NSIS installer with:
- Installation wizard
- Desktop shortcuts
- Start menu entries
- Uninstaller

## File Size Optimization

To reduce the executable size:

1. **Remove unused dependencies** from `requirements.txt`
2. **Exclude large packages** in `main.spec`
3. **Use UPX compression** (enabled by default)
4. **Remove development dependencies**

Expected sizes:
- Backend executable: 80-150 MB
- Frontend build: 2-5 MB
- Electron bundle: 70-100 MB
- Total portable .exe: 150-250 MB

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review build logs in console output
3. Check `electron/dist/` for build artifacts
4. Verify all prerequisites are installed

