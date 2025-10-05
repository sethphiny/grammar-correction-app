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
        npm install -g pnpm
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
    pip install -r requirements.txt
    
    # Download spaCy model
    print_status "Downloading spaCy English model..."
    python -m spacy download en_core_web_sm
    
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
    print_status "Installing Node.js dependencies..."
    pnpm install
    
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
