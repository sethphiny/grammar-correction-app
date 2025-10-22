#!/bin/bash

# Start Backend Development Server
# This script starts the FastAPI backend server in development mode

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "backend/main.py" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

print_status "Starting Grammar Correction Backend Server..."
echo

# Check if virtual environment exists
if [ ! -d "backend/venv" ]; then
    print_error "Virtual environment not found. Please run ./scripts/dev-setup.sh first"
    exit 1
fi

# Activate virtual environment
print_status "Activating virtual environment..."
# Detect if running on Git Bash on Windows
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source backend/venv/Scripts/activate
else
    source backend/venv/bin/activate
fi

# Check if LanguageTool is running (optional)
print_status "Checking LanguageTool connection..."
if curl -s http://localhost:8081/v2/languages > /dev/null 2>&1; then
    print_success "LanguageTool is running on localhost:8081"
else
    print_warning "LanguageTool is not running. Grammar checking will use fallback methods."
    print_warning "To start LanguageTool: docker run -d -p 8081:8081 silviof/docker-languagetool:latest"
fi

# Change to backend directory
cd backend

# Set environment variables
export PYTHONPATH=$(pwd)
export PYTHONUNBUFFERED=1

print_status "Starting FastAPI server with uvicorn..."
print_status "Backend will be available at: http://localhost:8000"
print_status "API documentation at: http://localhost:8000/docs"
print_status "Press Ctrl+C to stop the server"
echo

# Start the server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
