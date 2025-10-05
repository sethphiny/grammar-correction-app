#!/bin/bash

# Grammar Correction App - Start Frontend Server
# This script starts the React frontend server for local development

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

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "frontend/package.json" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

print_status "Starting Grammar Correction Frontend Server..."

cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    print_error "Dependencies not installed. Please run './scripts/dev-setup.sh' first"
    exit 1
fi

# Check if backend is running
print_status "Checking backend connection..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    print_success "Backend server is running ✓"
else
    print_warning "Backend server is not running at http://localhost:8000"
    print_status "Make sure to start the backend server first with './scripts/start-backend.sh'"
    echo ""
fi

# Start the frontend server
print_success "Starting React development server on http://localhost:3000"
print_status "The app will automatically open in your browser"
print_status "Press Ctrl+C to stop the server"
echo ""

npm start
