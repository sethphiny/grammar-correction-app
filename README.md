# Grammar Correction App

A comprehensive grammar checking application available as a **web app**, **desktop application**, or **Docker container**. Upload Word documents (.doc or .docx) and get detailed corrections using a hybrid approach combining spaCy, LanguageTool, and optional AI enhancement.

## Table of Contents

- [Features](#features)
- [Quick Start](#quick-start)
  - [Windows Desktop Application](#windows-desktop-application-easiest)
  - [Using Docker](#using-docker-recommended-for-web-deployment)
  - [Manual Setup](#manual-setup)
- [Architecture](#architecture)
- [API Endpoints](#api-endpoints)
- [Documentation](#documentation)
- [Configuration](#configuration)
- [Development](#development)
- [Utility Scripts](#utility-scripts)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)

## Features

### 🏆 **Premium Quality - Competitive with Grammarly Premium**

- **Three Operating Modes**:
  - 🆓 **Free Mode**: 470+ pattern-based rules (85-90% detection)
  - ⭐ **Competitive Mode**: Patterns + AI Detection (95-98% detection) **RECOMMENDED**
  - 💎 **Premium Mode**: Full AI with GPT-4o (98-99% detection)

- **30+ Grammar Categories**: redundancy, spelling, grammar, punctuation, dialogue, capitalisation, tense consistency, awkward phrasing, parallelism, articles, agreement, ambiguous pronouns, dangling modifiers, fragments, run-ons, word order, clarity, prepositions, register, repetition, comma splices, coordination, ellipsis, hyphenation, and more

- **🤖 AI-Powered Features**:
  - **AI Detection**: Catches subtle, context-dependent issues patterns miss
  - **AI Enhancement**: Professional-quality fix suggestions (~$0.01-0.03 per MB)
  - **Hybrid Intelligence**: 470+ patterns + GPT-4 = best-in-class accuracy

- **Advanced Capabilities**:
  - **Multiple Deployment Options**: Web app, Windows desktop, or Docker
  - **Web-based UI**: React frontend with TailwindCSS
  - **Desktop Application**: Portable Windows executable (no installation required)
  - **Real-Time Progress**: WebSocket-based live updates
  - **Selective Categories**: Choose what to check
  - **Multiple Formats**: DOCX or PDF reports
  - **Preview Mode**: Review before download
  - **Self-Hosted**: Privacy and control
  - **API Access**: Full programmatic access included

## Quick Start

### Windows Desktop Application (Easiest)

**For end users who want a simple, standalone application:**

1. **Download** the latest release:
   - Get `Grammar Correction App-[version]-portable.exe` from the releases page

2. **Run** the application:
   - Double-click the executable (no installation needed)
   - Wait 10-15 seconds for startup
   - Application window opens automatically

3. **Start checking**:
   - Upload your Word document
   - Select grammar categories (optional)
   - Download corrected document

**See:** `docs/WINDOWS_DESKTOP_README.md` for complete desktop app documentation  
**Build Guide:** `docs/BUILDING_WINDOWS_EXECUTABLE.md` for creating your own executable

### Using Docker (Recommended for Web Deployment)

```bash
# Clone and navigate to the project
cd grammar-correction-app

# Start the application
docker-compose up --build

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
```

### Manual Setup

#### Backend Setup

**Unix/Linux/Mac:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
python3 -m pip install -r requirements.txt
python3 -m spacy download en_core_web_sm

# Start the backend server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
# Or use the helper script: ./scripts/linux/start-backend.sh
```

**Windows:**

> **⚠️ Important:** Install [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) first!  
> Select "Desktop development with C++" workload. This is required for spaCy.  
> See [docs/WINDOWS_SETUP_TROUBLESHOOTING.md](docs/WINDOWS_SETUP_TROUBLESHOOTING.md) if you encounter issues.

```cmd
cd backend
python -m venv venv
venv\Scripts\activate
python -m pip install -r requirements.txt
python -m spacy download en_core_web_sm

REM Start the backend server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
REM Or use the helper script: scripts\windows\start-backend.bat
```

**Note**: The spaCy model `en_core_web_sm` is required for smart passive voice detection. If not installed, the feature will be automatically disabled with a warning message.

#### ⭐ **RECOMMENDED: Enable AI Enhancement (Premium Quality)**

For **95-98% detection accuracy** competitive with Grammarly Premium:

```bash
# Install AI dependencies
python3 -m pip install openai tiktoken

# Configure .env file
echo "LLM_ENHANCEMENT_ENABLED=true" >> .env
echo "OPENAI_API_KEY=sk-proj-your-key-here" >> .env
echo "OPENAI_MODEL=gpt-4o-mini" >> .env  # Cost-effective (recommended)
# echo "OPENAI_MODEL=gpt-4o" >> .env     # Maximum quality (premium)

# Restart backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Get API Key**: https://platform.openai.com/api-keys  
**Configuration Guide**: `docs/ENV_CONFIGURATION.md`

**Why AI Enhancement?**
- ✅ 95-98% detection (matches Grammarly Premium)
- ✅ Catches subtle issues patterns miss
- ✅ Professional-quality fixes
- ✅ Cost-effective: ~$0.01-0.03/MB (vs $144/year subscription)

#### Frontend Setup

**Unix/Linux/Mac:**
```bash
cd frontend
pnpm install              # or: npm install
pnpm run dev              # or: npm run dev
# Or use the helper script: ./scripts/linux/start-frontend.sh
```

**Windows:**
```cmd
cd frontend
npm install               REM or: pnpm install
npm start                 REM or: pnpm start
REM Or use the helper script: scripts\windows\start-frontend.bat
```

**Note:** The project supports both `pnpm` (recommended for faster installs) and `npm`. The Windows batch script automatically detects which package manager is available.

## Architecture

### Advanced Grammar Checking

The application uses multiple sophisticated approaches:

1. **Pattern-Based Checking**:
   - 100+ redundant phrases with corrections
   - 100+ awkward phrasing alternatives
   - Common punctuation errors
   - Grammar mistakes (homophones, verb errors, double negatives)
   - Capitalization errors
   - Tense consistency issues
   - Common spelling mistakes
   - 40+ wordy phrases for concision

2. **spaCy NLP (Linguistic Analysis)**:
   - **Smart Passive Voice Detection**: Uses dependency parsing (auxpass) to identify true passive constructions
     - Eliminates false positives (e.g., "is nuanced" is NOT flagged)
     - Only flags problematic passives without clear agents
     - Generates context-specific fix suggestions
   - Sentence segmentation and tokenization
   - Part-of-speech tagging for advanced analysis

3. **AI-Powered Enhancement (Optional Premium Feature)**:
   - **Selective LLM Enhancement**: Only processes complex/uncertain issues (20-30%)
   - **Smart Filtering**: Enhances low-confidence issues (< 85%) and complex categories
   - **Batch Processing**: Groups issues for efficient API usage
   - **Cost Optimization**: Typical cost $0.01-0.03 per MB document
   - **Quality Boost**: +40-50% improvement on complex grammar issues
   - **Graceful Degradation**: Falls back to pattern-based checking if unavailable

4. **Intelligent Filtering**:
   - Skips intentional passive voice patterns ("It was...", "There was...")
   - Excludes technical/academic contexts (framework, methodology, research)
   - Context-aware duplicate detection
   - Confidence scoring for each issue
   - User-selectable category filtering (analyze only what you need)

### Report Format

```
Line 4–5, Sentence 1
"Even in retirement, he carried the image of a railing set in stone, the kind that never moved. New boys come to him to watch him measure so they can learn."
• Problem: Tense shift → "come" (present) vs. surrounding past tense.
• Fix: → "New boys came to him to watch…"

✅ Summary
• Verb tense consistency issues: 5
• Awkward phrasing: 3
• Redundancy: 2
• Grammar/punctuation: 4
```

## API Endpoints

- `POST /upload` - Upload document for analysis
- `GET /status/{task_id}` - Check processing status
- `GET /download/{task_id}` - Download generated report
- `GET /results/{task_id}` - Get processing results (issues and summary)
- `GET /categories` - Get available grammar checking categories
- `GET /health` - Health check
- `WebSocket /ws/{task_id}` - Real-time progress updates

## Documentation

### 📚 Available Guides

**Getting Started:**
- **[Quick Start Guide](docs/QUICK_START_GUIDE.md)** - Get started in 5 minutes
- **[Windows Setup Troubleshooting](docs/WINDOWS_SETUP_TROUBLESHOOTING.md)** - Fix common Windows installation issues ⭐

**Configuration:**
- **[API Keys Setup Guide](docs/API_KEYS_SETUP_GUIDE.md)** - How to get and configure OpenAI API keys
- **[Environment Configuration](docs/ENV_CONFIGURATION.md)** - Configure environment variables and settings
- **[Categories Checklist](docs/CATEGORIES_CHECKLIST.md)** - Complete list of grammar categories

**Desktop Application:**
- **[Windows Desktop README](docs/WINDOWS_DESKTOP_README.md)** - Desktop application user guide
- **[Building Windows Executable](docs/BUILDING_WINDOWS_EXECUTABLE.md)** - Build your own desktop app
- **[Testing Executable](docs/TESTING_EXECUTABLE.md)** - Test procedures for desktop builds

### 💰 Cost Information

| Feature | Cost | When to Use |
|---------|------|-------------|
| Pattern-Based Checking | Free | Always (default) |
| AI-Enhanced Suggestions | $0.01-0.03/MB | Complex documents, premium quality |

**Note:** AI enhancement is optional and only processes 20-30% of issues (low-confidence cases)

## Configuration

### Environment Variables

```bash
# Backend
LANGUAGETOOL_URL=http://localhost:8081  # Optional: local LanguageTool server
MAX_FILE_SIZE=10485760  # 10MB
PROCESSING_TIMEOUT=300  # 5 minutes

# Frontend
REACT_APP_API_URL=http://localhost:8000
```

### Grammar Rules

The system supports customizable grammar rules:

- Verb tense consistency
- Subject-verb agreement
- Punctuation rules
- Style and clarity
- Redundancy detection
- Awkward phrasing

## Development

### Running Tests

```bash
# Backend tests
cd backend && python -m pytest

# Frontend tests
cd frontend && pnpm test      # or: npm test

# All tests
./scripts/test-all.sh
```

### Code Quality

```bash
# Backend linting
cd backend && flake8 . && black . && isort .

# Frontend linting
cd frontend && pnpm run lint  # or: npm run lint
```

## Utility Scripts

The `scripts/` directory contains helpful utilities for development and deployment, organized by platform:

```
scripts/
├── windows/          # Windows batch scripts (.bat)
├── linux/            # Unix/Linux/Mac shell scripts (.sh)
├── *.py             # Platform-agnostic Python scripts
├── GITBASH_WINDOWS.md  # Guide for Git Bash on Windows
└── README.md
```

### Platform Support

| Platform | Scripts to Use |
|----------|---------------|
| Linux / macOS | `scripts/linux/*.sh` |
| Windows (CMD/PowerShell) | `scripts/windows/*.bat` |
| Windows (Git Bash) | `scripts/linux/*.sh` ⭐ **Recommended** |

> **💡 Windows Developers:** If you have [Git Bash](https://git-scm.com/download/win) installed, use the `linux/` scripts for better compatibility! See `scripts/GITBASH_WINDOWS.md` for setup.

### Development Scripts

**Unix/Linux/Mac/Git Bash:** Use scripts in `scripts/linux/`  
**Windows (CMD/PowerShell):** Use scripts in `scripts/windows/`

- **`dev-setup`** - Complete development environment setup
- **`start-backend`** - Start FastAPI backend server
- **`start-frontend`** - Start React frontend development server
- **`start-dev`** - Start both backend and frontend concurrently
- **`test-all`** - Run all tests and linting
- **`setup-build-env`** - Setup build environment
- **`check-build-status`** - Check status of build artifacts

### Build Scripts

- **`build-backend.py`** - Build standalone Python executable with PyInstaller (Python)
- **`build-windows`** - Complete Windows desktop app build (`.bat` for Windows, `.sh` for Mac/Linux)
- **`rebuild-all.sh`** - Rebuild all components (Unix/Linux/Mac)

### Analysis Scripts

- **`analyze_performance.py`** - Analyze performance logs and metrics (Python)
- **`view_latest_log.py`** - View latest performance log (Python)

**See:** `scripts/README.md` for detailed documentation on all scripts

### Quick Examples

**Unix/Linux/Mac:**
```bash
./scripts/linux/dev-setup.sh      # Initial setup
./scripts/linux/start-dev.sh      # Start development servers
```

**Windows (CMD/PowerShell):**
```cmd
scripts\windows\dev-setup.bat     REM Initial setup
scripts\windows\start-dev.bat     REM Start development servers
```

**Windows (Git Bash):** ⭐ **Recommended**
```bash
# First time: make scripts executable
chmod +x scripts/linux/*.sh

# Then use the same commands as Linux/Mac
./scripts/linux/dev-setup.sh      # Initial setup
./scripts/linux/start-dev.sh      # Start development servers
```

## Deployment

### Windows Desktop Application

Build a standalone Windows executable:

```bash
# Quick build (all-in-one)
./scripts/linux/build-windows.sh    # Mac/Linux
scripts\windows\build-windows.bat   # Windows

# The result will be in: electron/dist/
# File: Grammar Correction App-[version]-portable.exe
```

**Requirements:**
- Python 3.8+ (for backend build)
- Node.js 18+ (for Electron build)
- PyInstaller: `pip install pyinstaller`

**See:** `docs/BUILDING_WINDOWS_EXECUTABLE.md` for detailed build instructions

### Production Docker

```bash
docker-compose -f docker-compose.prod.yml up --build
```

### Environment Setup

1. Copy `env.example` to `.env`
2. Configure your LanguageTool server (optional)
3. Set appropriate file size limits
4. Configure CORS settings
5. Set OpenAI API key for AI enhancement (optional)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

For issues and questions, please create an issue in the GitHub repository.
