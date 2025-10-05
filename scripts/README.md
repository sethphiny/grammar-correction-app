# Development Scripts

This directory contains scripts to help with local development and testing of the Grammar Correction App.

## 📋 Available Scripts

### Setup Scripts

#### `dev-setup.sh`
Sets up the complete development environment for local testing.

```bash
./scripts/dev-setup.sh
```

**What it does:**
- Checks Python 3.9+ and Node.js installations
- Creates Python virtual environment
- Installs all backend dependencies
- Installs all frontend dependencies
- Creates environment configuration files

### Development Scripts

#### `start-backend.sh`
Starts only the FastAPI backend server.

```bash
./scripts/start-backend.sh
```

**What it does:**
- Activates Python virtual environment
- Starts FastAPI server with hot reload
- Server runs on http://localhost:8000

#### `start-frontend.sh`
Starts only the React frontend server.

```bash
./scripts/start-frontend.sh
```

**What it does:**
- Checks if backend is running
- Starts React development server
- Server runs on http://localhost:3000

#### `start-dev.sh`
Starts both backend and frontend servers simultaneously.

```bash
./scripts/start-dev.sh
```

**What it does:**
- Starts backend server in background
- Starts frontend server
- Provides unified access to both services
- Handles graceful shutdown with Ctrl+C

### Testing Scripts

#### `test-backend.sh`
Runs backend API tests.

```bash
./scripts/test-backend.sh
```

**What it does:**
- Installs test dependencies (pytest, httpx)
- Creates basic API test suite
- Runs all backend tests
- Provides manual testing instructions

#### `test-frontend.sh`
Runs frontend React tests.

```bash
./scripts/test-frontend.sh
```

**What it does:**
- Creates basic React test suite
- Runs Jest tests
- Provides manual testing instructions

#### `test-all.sh`
Runs all tests for both backend and frontend.

```bash
./scripts/test-all.sh
```

**What it does:**
- Runs backend tests
- Runs frontend tests
- Provides comprehensive test summary
- Shows next steps for development

## 🚀 Quick Start Guide

### First Time Setup

1. **Clone the repository** (if not already done)
2. **Run the setup script:**
   ```bash
   ./scripts/dev-setup.sh
   ```

### Daily Development

**Option 1: Start both servers**
```bash
./scripts/start-dev.sh
```

**Option 2: Start servers separately**
```bash
# Terminal 1 - Backend
./scripts/start-backend.sh

# Terminal 2 - Frontend  
./scripts/start-frontend.sh
```

### Testing

**Run all tests:**
```bash
./scripts/test-all.sh
```

**Run specific tests:**
```bash
./scripts/test-backend.sh
./scripts/test-frontend.sh
```

## 🌐 Access Points

After starting the servers:

- **Frontend Application**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 📁 Project Structure

```
grammar-correction-app/
├── scripts/
│   ├── dev-setup.sh      # Initial setup
│   ├── start-backend.sh  # Backend server
│   ├── start-frontend.sh # Frontend server
│   ├── start-dev.sh      # Both servers
│   ├── test-backend.sh   # Backend tests
│   ├── test-frontend.sh  # Frontend tests
│   ├── test-all.sh       # All tests
│   └── README.md         # This file
├── backend/              # FastAPI backend
├── frontend/             # React frontend
├── docker/               # Docker configurations
└── docker-compose.yml    # Docker Compose setup
```

## 🔧 Environment Configuration

The scripts automatically create environment files:

**Backend (.env):**
```env
PYTHONPATH=/app
PYTHONUNBUFFERED=1
LANGUAGETOOL_HOST=localhost
LANGUAGETOOL_PORT=8081
```

**Frontend (.env):**
```env
REACT_APP_API_URL=http://localhost:8000
GENERATE_SOURCEMAP=false
```

## 🐛 Troubleshooting

### Common Issues

1. **Permission Denied**
   ```bash
   chmod +x scripts/*.sh
   ```

2. **Python/Node Not Found**
   - Install Python 3.9+ and Node.js 16+
   - Make sure they're in your PATH

3. **Dependencies Not Found**
   ```bash
   ./scripts/dev-setup.sh
   ```

4. **Port Already in Use**
   - Backend (8000): Kill process or change port
   - Frontend (3000): Kill process or change port

5. **Backend Connection Failed**
   - Make sure backend is running first
   - Check http://localhost:8000/health

### Manual Testing

**Test API endpoints:**
```bash
# Health check
curl http://localhost:8000/health

# File upload (replace with your file)
curl -X POST 'http://localhost:8000/upload' \
     -F 'file=@test.docx' \
     -F 'output_format=docx'
```

**Test frontend:**
1. Open http://localhost:3000
2. Upload a Word document
3. Check progress tracking
4. Download generated report

## 📝 Development Workflow

1. **Setup** (once): `./scripts/dev-setup.sh`
2. **Develop**: `./scripts/start-dev.sh`
3. **Test**: `./scripts/test-all.sh`
4. **Deploy**: Use Docker with `docker-compose up --build`

## 🤝 Contributing

When adding new features:

1. Update relevant test files
2. Run tests: `./scripts/test-all.sh`
3. Test manually with real documents
4. Update this README if needed
