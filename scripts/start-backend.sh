#!/bin/bash

# Grammar Correction App - Start Backend Server
# This script starts the FastAPI backend server for local development

set -e  # Exit on any error

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

# Check if we're in the right directory
if [ ! -f "backend/main.py" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

print_status "Starting Grammar Correction Backend Server..."

cd backend

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    print_error "Virtual environment not found. Please run './scripts/dev-setup.sh' first"
    exit 1
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Set Java 17 environment variables for LanguageTool
print_status "Setting up Java 17 environment for LanguageTool..."
export JAVA_HOME="/usr/local/opt/openjdk@17"
export PATH="/usr/local/opt/openjdk@17/bin:$PATH"

# Check if dependencies are installed
if ! python -c "import fastapi" 2>/dev/null; then
    print_error "Dependencies not installed. Please run './scripts/dev-setup.sh' first"
    exit 1
fi

# Create necessary directories
mkdir -p /tmp/grammar-uploads
mkdir -p /tmp/grammar-reports

# Start the server
print_success "Starting FastAPI server on http://localhost:8000"
print_status "API documentation available at http://localhost:8000/docs"
print_status "Press Ctrl+C to stop the server"
echo ""

uvicorn main:app --reload --host 0.0.0.0 --port 8000
