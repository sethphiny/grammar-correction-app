# Linux/Unix/Mac Scripts

This directory contains shell scripts (.sh) for Unix-like systems (Linux, macOS, BSD, etc.).

## Available Scripts

### Development

- **`dev-setup.sh`** - Initial development environment setup
- **`start-backend.sh`** - Start FastAPI backend server
- **`start-frontend.sh`** - Start React frontend server
- **`start-dev.sh`** - Start both backend and frontend

### Testing

- **`test-all.sh`** - Run all tests and code quality checks

### Building

- **`build-windows.sh`** - Build Windows desktop application (cross-platform)
- **`setup-build-env.sh`** - Setup build environment
- **`check-build-status.sh`** - Check build artifact status
- **`rebuild-all.sh`** - Rebuild all components
- **`make-executable.sh`** - Make scripts executable

## Quick Start

```bash
# From project root:

# 1. Make scripts executable (first time only)
chmod +x scripts/linux/*.sh

# 2. Initial setup
./scripts/linux/dev-setup.sh

# 3. Start development servers
./scripts/linux/start-dev.sh

# 4. Run tests
./scripts/linux/test-all.sh

# 5. Build desktop app
./scripts/linux/build-windows.sh
```

## Requirements

- Unix-like OS (Linux, macOS, BSD, WSL)
- Python 3.9+
- Node.js 18+
- pnpm (recommended) or npm
- Docker (optional, for LanguageTool)

## Notes

- All scripts should be run from the project root directory
- Scripts need execute permissions: `chmod +x scripts/linux/*.sh`
- Virtual environment will be created automatically by dev-setup.sh
- Most scripts check for requirements and provide helpful error messages

## Documentation

See the main [scripts/README.md](../README.md) for detailed documentation.

