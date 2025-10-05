# Development Scripts

This directory contains various scripts to help with development, testing, and deployment of the Grammar Correction App.

## Available Scripts

### Setup Scripts

#### `dev-setup.sh`
Sets up the complete development environment.

```bash
./scripts/dev-setup.sh
```

**What it does:**
- Checks system requirements (Python 3.9+, Node.js 18+, pnpm, Docker)
- Creates Python virtual environment
- Installs backend dependencies
- Downloads spaCy English model
- Installs frontend dependencies
- Creates environment configuration files
- Sets up LanguageTool (optional)

### Development Scripts

#### `start-backend.sh`
Starts the FastAPI backend server in development mode.

```bash
./scripts/start-backend.sh
```

**What it does:**
- Activates Python virtual environment
- Checks LanguageTool connection
- Starts uvicorn server with auto-reload
- Backend available at: http://localhost:8000
- API docs at: http://localhost:8000/docs

#### `start-frontend.sh`
Starts the React frontend development server.

```bash
./scripts/start-frontend.sh
```

**What it does:**
- Checks backend connection
- Starts React development server
- Frontend available at: http://localhost:3000

#### `start-dev.sh`
Starts both backend and frontend servers concurrently.

```bash
./scripts/start-dev.sh
```

**What it does:**
- Starts LanguageTool with Docker (if not running)
- Starts backend server in background
- Starts frontend server in background
- Provides logs and status information
- Handles graceful shutdown with Ctrl+C

### Testing Scripts

#### `test-all.sh`
Runs all tests and code quality checks.

```bash
./scripts/test-all.sh
```

**What it does:**
- Runs backend unit tests with pytest
- Runs frontend tests with Jest
- Performs code linting (flake8, black, isort for Python; ESLint for TypeScript)
- Runs integration tests
- Generates coverage reports

## Usage Examples

### Quick Start Development

1. **Initial Setup** (run once):
   ```bash
   ./scripts/dev-setup.sh
   ```

2. **Start Development Environment**:
   ```bash
   ./scripts/start-dev.sh
   ```

3. **Run Tests**:
   ```bash
   ./scripts/test-all.sh
   ```

### Individual Services

**Backend only:**
```bash
./scripts/start-backend.sh
```

**Frontend only:**
```bash
./scripts/start-frontend.sh
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
