# Development Scripts

This directory contains various scripts to help with development, testing, and deployment of the Grammar Correction App.

## Directory Structure

```
scripts/
├── windows/              # Windows batch scripts (.bat)
│   ├── dev-setup.bat
│   ├── start-backend.bat
│   ├── start-frontend.bat
│   ├── start-dev.bat
│   ├── test-all.bat
│   ├── build-windows.bat
│   ├── setup-build-env.bat
│   ├── check-build-status.bat
│   └── README.md
│
├── linux/                # Unix/Linux/Mac shell scripts (.sh)
│   ├── dev-setup.sh     # Also works with Git Bash on Windows!
│   ├── start-backend.sh
│   ├── start-frontend.sh
│   ├── start-dev.sh
│   ├── test-all.sh
│   ├── build-windows.sh
│   ├── setup-build-env.sh
│   ├── check-build-status.sh
│   ├── rebuild-all.sh
│   ├── make-executable.sh
│   └── README.md
│
├── analyze_performance.py  # Platform-agnostic Python scripts
├── build-backend.py
├── view_latest_log.py
├── GITBASH_WINDOWS.md   # Guide for using Git Bash on Windows
└── README.md
```

## Platform Support

| Platform | Scripts to Use | Notes |
|----------|---------------|-------|
| **Linux** | `linux/*.sh` | Native shell scripts |
| **macOS** | `linux/*.sh` | Native shell scripts |
| **Windows (CMD/PowerShell)** | `windows/*.bat` | Native batch scripts |
| **Windows (Git Bash)** | `linux/*.sh` | ✨ Recommended for Windows developers! |

> **💡 Windows Users:** If you have Git Bash installed, we recommend using the `linux/*.sh` scripts for better compatibility and features. See [GITBASH_WINDOWS.md](GITBASH_WINDOWS.md) for details.

## Available Scripts

### Setup Scripts

#### `dev-setup.sh` / `dev-setup.bat`
Sets up the complete development environment.

**Unix/Linux/Mac:**
```bash
./scripts/linux/dev-setup.sh
```

**Windows:**
```cmd
scripts\windows\dev-setup.bat
```

**What it does:**
- Checks system requirements (Python 3.9+, Node.js 18+, npm/pnpm)
- Creates Python virtual environment
- Installs backend dependencies
- Downloads spaCy English model
- Installs frontend dependencies
- Creates environment configuration files
- Verifies setup

**Note:** This script only sets up the development environment. Use `start-backend.sh` and `start-frontend.sh` to run the servers.

### Development Scripts

#### `start-backend.sh` / `start-backend.bat`
Starts the FastAPI backend server in development mode.

**Unix/Linux/Mac:**
```bash
./scripts/linux/start-backend.sh
```

**Windows:**
```cmd
scripts\windows\start-backend.bat
```

**What it does:**
- Activates Python virtual environment
- Checks LanguageTool connection
- Starts uvicorn server with auto-reload
- Backend available at: http://localhost:8000
- API docs at: http://localhost:8000/docs

#### `start-frontend.sh` / `start-frontend.bat`
Starts the React frontend development server.

**Unix/Linux/Mac:**
```bash
./scripts/linux/start-frontend.sh
```

**Windows:**
```cmd
scripts\windows\start-frontend.bat
```

**What it does:**
- Checks backend connection
- Starts React development server
- Uses pnpm if available, otherwise npm
- Frontend available at: http://localhost:3000

#### `start-dev.sh` / `start-dev.bat`
Starts both backend and frontend servers concurrently.

**Unix/Linux/Mac:**
```bash
./scripts/linux/start-dev.sh
```

**Windows:**
```cmd
scripts\windows\start-dev.bat
```

**What it does:**
- Starts LanguageTool with Docker (if not running)
- Starts backend server (new window on Windows, background on Unix)
- Starts frontend server (new window on Windows, background on Unix)
- Provides logs and status information
- Handles graceful shutdown with Ctrl+C

### Testing Scripts

#### `test-all.sh` / `test-all.bat`
Runs all tests and code quality checks.

**Unix/Linux/Mac:**
```bash
./scripts/linux/test-all.sh
```

**Windows:**
```cmd
scripts\windows\test-all.bat
```

**What it does:**
- Runs backend unit tests with pytest
- Runs frontend tests with Jest
- Performs code linting (flake8, black, isort for Python; ESLint for TypeScript)
- Runs integration tests
- Generates coverage reports

## Usage Examples

### Quick Start Development

#### Unix/Linux/Mac

1. **Initial Setup** (run once):
   ```bash
   # Make scripts executable
   chmod +x scripts/linux/*.sh
   
   # Install all dependencies
   ./scripts/linux/dev-setup.sh
   ```

2. **Start Development Servers**:
   ```bash
   # Option A: Start both servers at once
   ./scripts/linux/start-dev.sh
   
   # Option B: Start servers individually (in separate terminals)
   ./scripts/linux/start-backend.sh    # Terminal 1
   ./scripts/linux/start-frontend.sh   # Terminal 2
   ```

3. **Run Tests**:
   ```bash
   ./scripts/linux/test-all.sh
   ```

4. **(Optional) Start LanguageTool**:
   ```bash
   docker run -d -p 8081:8081 silviof/docker-languagetool:latest
   ```

#### Windows

1. **Initial Setup** (run once):
   ```cmd
   scripts\windows\dev-setup.bat
   ```

2. **Start Development Environment**:
   ```cmd
   scripts\windows\start-dev.bat
   ```

3. **Run Tests**:
   ```cmd
   scripts\windows\test-all.bat
   ```

### Individual Services

#### Unix/Linux/Mac

**Backend only:**
```bash
./scripts/linux/start-backend.sh
```

**Frontend only:**
```bash
./scripts/linux/start-frontend.sh
```

#### Windows

**Backend only:**
```cmd
scripts\windows\start-backend.bat
```

**Frontend only:**
```cmd
scripts\windows\start-frontend.bat
```

### Docker Development

**Start with Docker Compose:**
```bash
docker-compose up --build
```

**Production deployment:**
```bash
docker-compose -f docker-compose.prod.yml up --build
```

## Environment Configuration

### Backend Environment Variables

Create `backend/.env`:
```bash
LANGUAGETOOL_URL=http://localhost:8081
MAX_FILE_SIZE=10485760
PROCESSING_TIMEOUT=300
CORS_ORIGINS=http://localhost:3000
DEBUG=true
LOG_LEVEL=INFO
```

### Frontend Environment Variables

Create `frontend/.env`:
```bash
REACT_APP_API_URL=http://localhost:8000
```

## Troubleshooting

### Common Issues

1. **Python virtual environment not found:**
   ```bash
   ./scripts/dev-setup.sh
   ```

2. **Node modules not found:**
   ```bash
   cd frontend && pnpm install
   ```

3. **LanguageTool connection failed:**
   ```bash
   docker run -d -p 8081:8081 silviof/docker-languagetool:latest
   ```

4. **Port already in use:**
   - Backend (8000): Kill process using port 8000
   - Frontend (3000): Kill process using port 3000
   - LanguageTool (8081): Kill Docker container

### Log Files

When using `start-dev.sh`, logs are saved to:
- `backend.log` - Backend server logs
- `frontend.log` - Frontend server logs

View logs:
```bash
tail -f backend.log
tail -f frontend.log
```

### Health Checks

Check if services are running:

**Backend:**
```bash
curl http://localhost:8000/health
```

**LanguageTool:**
```bash
curl http://localhost:8081/v2/languages
```

**Frontend:**
```bash
curl http://localhost:3000
```

## Script Permissions

Make scripts executable:
```bash
chmod +x scripts/*.sh
```

## Dependencies

### System Requirements
- Python 3.9+
- Node.js 18+
- pnpm
- Docker (optional, for LanguageTool)
- Docker Compose (optional, for full stack)

### Python Dependencies
- FastAPI
- uvicorn
- python-docx
- reportlab
- language-tool-python
- spacy
- textract
- pytest (for testing)

### Node.js Dependencies
- React 18
- TypeScript
- TailwindCSS
- Axios
- React Dropzone
- Lucide React

## Contributing

When adding new scripts:

1. Follow the existing naming convention
2. Add proper error handling
3. Include colored output for better UX
4. Add documentation to this README
5. Make scripts executable
6. Test on both macOS and Linux
