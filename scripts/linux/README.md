# Linux/Unix/Mac Scripts

This directory contains shell scripts (.sh) for Unix-like systems (Linux, macOS, BSD, etc.).

> **✨ Also works with Git Bash on Windows!** These scripts automatically detect Git Bash and work seamlessly on Windows. See [../GITBASH_WINDOWS.md](../GITBASH_WINDOWS.md) for setup guide.

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

# 2. Initial setup (installs dependencies only)
./scripts/linux/dev-setup.sh

# 3. Start development servers
./scripts/linux/start-dev.sh        # Start both backend & frontend
# OR start them individually:
./scripts/linux/start-backend.sh    # Terminal 1
./scripts/linux/start-frontend.sh   # Terminal 2

# 4. (Optional) Start LanguageTool
docker run -d -p 8081:8081 silviof/docker-languagetool:latest

# 5. Run tests
./scripts/linux/test-all.sh

# 6. Build desktop app
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
- `dev-setup.sh` only installs dependencies - it does NOT start servers
- Use `start-backend.sh` and `start-frontend.sh` to run the servers
- Virtual environment will be created automatically by dev-setup.sh
- Docker is optional - only needed for LanguageTool (grammar checking works without it)
- Most scripts check for requirements and provide helpful error messages

## Documentation

See the main [scripts/README.md](../README.md) for detailed documentation.

