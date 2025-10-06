#!/bin/bash

# Grammar Correction App - Development Setup Script
# This script sets up the development environment for the Grammar Correction App

set -e

echo "🚀 Setting up Grammar Correction App Development Environment"
echo "============================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if required tools are installed
check_requirements() {
    print_status "Checking system requirements..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed. Please install Python 3.9 or higher."
        exit 1
    fi
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        print_error "Node.js is not installed. Please install Node.js 18 or higher."
        exit 1
    fi
    
    # Check pnpm
    if ! command -v pnpm &> /dev/null; then
        print_warning "pnpm is not installed. Installing pnpm..."
        if npm install -g pnpm; then
            print_success "pnpm installed successfully"
        else
            print_error "Failed to install pnpm. Please install it manually: npm install -g pnpm"
            exit 1
        fi
    else
        print_success "pnpm is available"
    fi
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_warning "Docker is not installed. Docker is required for running the full application."
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        print_warning "Docker Compose is not installed. Docker Compose is required for running the full application."
    fi
    
    print_success "System requirements check completed"
}

# Setup backend environment
setup_backend() {
    print_status "Setting up backend environment..."
    
    cd backend
    
    # Create virtual environment
    if [ ! -d "venv" ]; then
        print_status "Creating Python virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install dependencies
    print_status "Installing Python dependencies..."
    if ! pip install -r requirements.txt; then
        print_error "Failed to install Python dependencies"
        exit 1
    fi
    
    # Download spaCy model
    print_status "Downloading spaCy English model..."
    if ! python -c "import spacy; spacy.load('en_core_web_sm')" 2>/dev/null; then
        print_status "Installing spaCy English model..."
        # Try direct download if spacy CLI fails
        pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl
        print_success "spaCy English model installed successfully"
    else
        print_success "spaCy English model already available"
    fi
    
    # Create necessary directories
    mkdir -p temp_files uploads
    
    print_success "Backend environment setup completed"
    cd ..
}

# Setup frontend environment
setup_frontend() {
    print_status "Setting up frontend environment..."
    
    cd frontend
    
    # Install dependencies
    print_status "Installing Node.js dependencies with pnpm..."
    
    # Check if node_modules exists, if so clean it first
    if [ -d "node_modules" ]; then
        print_status "Cleaning existing node_modules..."
        rm -rf node_modules
    fi
    
    # Install with pnpm, using strict-peer-dependencies=false to handle TypeScript conflicts
    if ! pnpm install --no-strict-peer-dependencies; then
        print_warning "pnpm install failed, trying with force flag..."
        pnpm install --force --no-strict-peer-dependencies
    fi
    
    print_success "Frontend environment setup completed"
    cd ..
}

# Create environment files
setup_environment() {
    print_status "Setting up environment files..."
    
    # Copy example environment file if it doesn't exist
    if [ ! -f ".env" ]; then
        cp env.example .env
        print_success "Created .env file from env.example"
    else
        print_warning ".env file already exists, skipping..."
    fi
    
    # Create backend .env if it doesn't exist
    if [ ! -f "backend/.env" ]; then
        cat > backend/.env << EOF
LANGUAGETOOL_URL=http://localhost:8081
MAX_FILE_SIZE=10485760
PROCESSING_TIMEOUT=300
CORS_ORIGINS=http://localhost:3000
DEBUG=true
LOG_LEVEL=INFO
EOF
        print_success "Created backend/.env file"
    fi
    
    # Create frontend .env if it doesn't exist
    if [ ! -f "frontend/.env" ]; then
        cat > frontend/.env << EOF
REACT_APP_API_URL=http://localhost:8000
EOF
        print_success "Created frontend/.env file"
    fi
}

# Setup LanguageTool (optional)
setup_languagetool() {
    print_status "Setting up LanguageTool..."
    
    # Check if LanguageTool is already running
    if curl -s http://localhost:8081/v2/languages > /dev/null 2>&1; then
        print_success "LanguageTool is already running on localhost:8081"
        return
    fi
    
    print_warning "LanguageTool is not running. You can start it with:"
    print_warning "  docker run -d -p 8081:8081 silviof/docker-languagetool:latest"
    print_warning "  or use the docker-compose setup"
}

# Verify setup
verify_setup() {
    print_status "Verifying setup..."
    
    # Verify backend
    cd backend
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
        if python -c "import spacy; nlp = spacy.load('en_core_web_sm'); print('✓ spaCy model loaded')" 2>/dev/null; then
            print_success "Backend spaCy model verified"
        else
            print_warning "Backend spaCy model verification failed"
        fi
        if python -c "from services.hybrid_grammar_checker import HybridGrammarChecker; print('✓ Grammar checker imports successfully')" 2>/dev/null; then
            print_success "Backend grammar checker verified"
        else
            print_warning "Backend grammar checker verification failed"
        fi
    else
        print_warning "Backend virtual environment not found"
    fi
    cd ..
    
    # Verify frontend
    cd frontend
    if [ -d "node_modules" ] && [ -f "package.json" ]; then
        print_success "Frontend dependencies verified"
    else
        print_warning "Frontend dependencies verification failed"
    fi
    cd ..
    
    print_success "Setup verification completed"
}

# Main setup function
main() {
    echo
    print_status "Starting development environment setup..."
    echo
    
    check_requirements
    echo
    
    setup_environment
    echo
    
    setup_backend
    echo
    
    setup_frontend
    echo
    
    setup_languagetool
    echo
    
    # Verify setup
    verify_setup
    echo
    
    print_success "🎉 Development environment setup completed!"
    echo
    print_status "Next steps:"
    echo "1. Start LanguageTool (optional): docker run -d -p 8081:8081 silviof/docker-languagetool:latest"
    echo "2. Start backend: ./scripts/start-backend.sh"
    echo "3. Start frontend: ./scripts/start-frontend.sh"
    echo "4. Or start everything with Docker: docker-compose up --build"
    echo
    print_status "The application will be available at:"
    echo "- Frontend: http://localhost:3000"
    echo "- Backend API: http://localhost:8000"
    echo "- API Documentation: http://localhost:8000/docs"
    echo
}

# Run main function
main "$@"
