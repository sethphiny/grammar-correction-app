#!/bin/bash

# Start Frontend Development Server
# This script starts the React frontend development server

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
if [ ! -f "frontend/package.json" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

print_status "Starting Grammar Correction Frontend Server..."
echo

# Check if node_modules exists
if [ ! -d "frontend/node_modules" ]; then
    print_error "Node modules not found. Please run ./scripts/dev-setup.sh first"
    exit 1
fi

# Check if pnpm is available
if ! command -v pnpm &> /dev/null; then
    print_error "pnpm is not installed. Please install pnpm first:"
    print_error "npm install -g pnpm"
    exit 1
fi

# Change to frontend directory
cd frontend

# Check if backend is running
print_status "Checking backend connection..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    print_success "Backend is running on localhost:8000"
else
    print_warning "Backend is not running. Please start it with: ./scripts/start-backend.sh"
    print_warning "Frontend will still start but API calls will fail."
fi

print_status "Starting React development server..."
print_status "Frontend will be available at: http://localhost:3000"
print_status "Press Ctrl+C to stop the server"
echo

# Start the development server
pnpm start
