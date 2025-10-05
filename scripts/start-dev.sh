#!/bin/bash

# Grammar Correction App - Start Development Environment
# This script starts both backend and frontend servers for local development

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
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

print_header() {
    echo -e "${PURPLE}[HEADER]${NC} $1"
}

# Function to cleanup background processes
cleanup() {
    print_status "Shutting down servers..."
    jobs -p | xargs -r kill
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Check if we're in the right directory
if [ ! -f "backend/main.py" ] || [ ! -f "frontend/package.json" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

print_header "🚀 Starting Grammar Correction App Development Environment"
echo ""

# Check if setup has been run
if [ ! -d "backend/venv" ] || [ ! -d "frontend/node_modules" ]; then
    print_warning "Development environment not set up. Running setup first..."
    ./scripts/dev-setup.sh
    echo ""
fi

# Create necessary directories
mkdir -p /tmp/grammar-uploads
mkdir -p /tmp/grammar-reports

print_status "Starting backend server in background..."
cd backend
source venv/bin/activate

# Set Java 17 environment variables for LanguageTool
export JAVA_HOME="/usr/local/opt/openjdk@17"
export PATH="/usr/local/opt/openjdk@17/bin:$PATH"

uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

# Wait a moment for backend to start
sleep 3

# Check if backend started successfully
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    print_error "Backend server failed to start"
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
fi

print_success "Backend server started ✓ (PID: $BACKEND_PID)"

print_status "Starting frontend server..."
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

print_success "Frontend server started ✓ (PID: $FRONTEND_PID)"

echo ""
print_header "🎉 Development environment is ready!"
echo ""
echo "📱 Access points:"
echo "  • Frontend: http://localhost:3000"
echo "  • Backend API: http://localhost:8000"
echo "  • API Documentation: http://localhost:8000/docs"
echo ""
echo "📋 Server status:"
echo "  • Backend PID: $BACKEND_PID"
echo "  • Frontend PID: $FRONTEND_PID"
echo ""
print_status "Press Ctrl+C to stop both servers"
echo ""

# Wait for user to stop
wait
