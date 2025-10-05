#!/bin/bash

# Start Development Environment
# This script starts both backend and frontend servers concurrently

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
if [ ! -f "backend/main.py" ] || [ ! -f "frontend/package.json" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

print_status "Starting Grammar Correction App Development Environment..."
echo

# Function to cleanup background processes
cleanup() {
    print_status "Shutting down servers..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Check if LanguageTool is running
print_status "Checking LanguageTool connection..."
if curl -s http://localhost:8081/v2/languages > /dev/null 2>&1; then
    print_success "LanguageTool is running on localhost:8081"
else
    print_warning "LanguageTool is not running. Starting with Docker..."
    docker run -d -p 8081:8081 --name languagetool silviof/docker-languagetool:latest || true
    sleep 5
    if curl -s http://localhost:8081/v2/languages > /dev/null 2>&1; then
        print_success "LanguageTool started successfully"
    else
        print_warning "LanguageTool failed to start. Grammar checking will use fallback methods."
    fi
fi

# Start backend in background
print_status "Starting backend server..."
cd backend
source venv/bin/activate
export PYTHONPATH=$(pwd)
export PYTHONUNBUFFERED=1
uvicorn main:app --reload --host 0.0.0.0 --port 8000 > ../backend.log 2>&1 &
BACKEND_PID=$!
cd ..

# Wait a moment for backend to start
sleep 3

# Check if backend started successfully
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    print_success "Backend started successfully on http://localhost:8000"
else
    print_warning "Backend may not have started properly. Check backend.log for details."
fi

# Start frontend in background
print_status "Starting frontend server..."
cd frontend
pnpm start > ../frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

# Wait a moment for frontend to start
sleep 5

print_success "🎉 Development environment started!"
echo
print_status "Services running:"
echo "- Backend API: http://localhost:8000"
echo "- Frontend App: http://localhost:3000"
echo "- API Documentation: http://localhost:8000/docs"
echo
print_status "Logs:"
echo "- Backend: tail -f backend.log"
echo "- Frontend: tail -f frontend.log"
echo
print_status "Press Ctrl+C to stop all servers"
echo

# Wait for user to stop
wait
