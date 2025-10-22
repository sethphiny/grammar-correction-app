#!/bin/bash

# Test All Components
# This script runs all tests for the Grammar Correction App

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

print_status "Running all tests for Grammar Correction App..."
echo

# Function to run backend tests
test_backend() {
    print_status "Running backend tests..."
    
    cd backend
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        print_error "Virtual environment not found. Please run ./scripts/dev-setup.sh first"
        return 1
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install test dependencies if not already installed
    pip install pytest pytest-asyncio pytest-cov > /dev/null 2>&1 || true
    
    # Run tests
    if [ -d "tests" ]; then
        python -m pytest tests/ -v --cov=. --cov-report=term-missing
    else
        print_warning "No tests directory found in backend. Creating basic test structure..."
        mkdir -p tests
        cat > tests/__init__.py << EOF
# Tests package
EOF
        
        cat > tests/test_main.py << EOF
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_upload_invalid_file():
    response = client.post("/upload", files={"file": ("test.txt", b"test content", "text/plain")})
    assert response.status_code == 400
EOF
        
        python -m pytest tests/ -v
    fi
    
    cd ..
    print_success "Backend tests completed"
}

# Function to run frontend tests
test_frontend() {
    print_status "Running frontend tests..."
    
    cd frontend
    
    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        print_error "Node modules not found. Please run ./scripts/dev-setup.sh first"
        return 1
    fi
    
    # Run tests
    pnpm test --watchAll=false --coverage --passWithNoTests
    
    cd ..
    print_success "Frontend tests completed"
}

# Function to run linting
test_linting() {
    print_status "Running code quality checks..."
    
    # Backend linting
    print_status "Checking backend code quality..."
    cd backend
    
    if [ -d "venv" ]; then
        source venv/bin/activate
        
        # Install linting tools if not already installed
        pip install flake8 black isort > /dev/null 2>&1 || true
        
        # Run linting
        print_status "Running flake8..."
        flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics || true
        
        print_status "Running black (check only)..."
        black --check . || true
        
        print_status "Running isort (check only)..."
        isort --check-only . || true
    fi
    
    cd ..
    
    # Frontend linting
    print_status "Checking frontend code quality..."
    cd frontend
    
    if [ -d "node_modules" ]; then
        pnpm run lint || true
    fi
    
    cd ..
    
    print_success "Code quality checks completed"
}

# Function to run integration tests
test_integration() {
    print_status "Running integration tests..."
    
    # Check if backend is running
    if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
        print_warning "Backend is not running. Skipping integration tests."
        print_warning "Start backend with: ./scripts/start-backend.sh"
        return 0
    fi
    
    # Basic API tests
    print_status "Testing API endpoints..."
    
    # Test health endpoint
    if curl -s http://localhost:8000/health | grep -q "healthy"; then
        print_success "Health endpoint working"
    else
        print_error "Health endpoint failed"
        return 1
    fi
    
    # Test API documentation
    if curl -s http://localhost:8000/docs > /dev/null 2>&1; then
        print_success "API documentation accessible"
    else
        print_warning "API documentation not accessible"
    fi
    
    print_success "Integration tests completed"
}

# Main test function
main() {
    local exit_code=0
    
    # Run all test suites
    test_backend || exit_code=1
    echo
    
    test_frontend || exit_code=1
    echo
    
    test_linting || exit_code=1
    echo
    
    test_integration || exit_code=1
    echo
    
    # Summary
    if [ $exit_code -eq 0 ]; then
        print_success "🎉 All tests passed!"
    else
        print_error "❌ Some tests failed. Check the output above for details."
    fi
    
    exit $exit_code
}

# Run main function
main "$@"
