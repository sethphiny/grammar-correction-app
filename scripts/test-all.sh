#!/bin/bash

# Grammar Correction App - Test All
# This script runs all tests for both backend and frontend

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

print_header() {
    echo -e "${PURPLE}================================${NC}"
    echo -e "${PURPLE}$1${NC}"
    echo -e "${PURPLE}================================${NC}"
}

print_section() {
    echo -e "${BLUE}--------------------------------${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}--------------------------------${NC}"
}

# Check if we're in the right directory
if [ ! -f "backend/main.py" ] || [ ! -f "frontend/package.json" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

print_header "🧪 Running All Tests for Grammar Correction App"
echo ""

# Track test results
BACKEND_TESTS_PASSED=true
FRONTEND_TESTS_PASSED=true

# Test backend
print_section "Testing Backend"
if ./scripts/test-backend.sh; then
    print_success "Backend tests passed ✓"
else
    print_error "Backend tests failed ✗"
    BACKEND_TESTS_PASSED=false
fi

echo ""

# Test frontend
print_section "Testing Frontend"
if ./scripts/test-frontend.sh; then
    print_success "Frontend tests passed ✓"
else
    print_error "Frontend tests failed ✗"
    FRONTEND_TESTS_PASSED=false
fi

echo ""

# Summary
print_header "📊 Test Summary"

if [ "$BACKEND_TESTS_PASSED" = true ] && [ "$FRONTEND_TESTS_PASSED" = true ]; then
    print_success "🎉 All tests passed! The application is ready for development."
    echo ""
    print_status "Next steps:"
    echo "  • Run './scripts/start-dev.sh' to start the development environment"
    echo "  • Access the app at http://localhost:3000"
    echo "  • API docs at http://localhost:8000/docs"
    exit 0
else
    print_error "❌ Some tests failed. Please fix the issues before proceeding."
    echo ""
    if [ "$BACKEND_TESTS_PASSED" = false ]; then
        echo "  • Backend tests failed - check the output above"
    fi
    if [ "$FRONTEND_TESTS_PASSED" = false ]; then
        echo "  • Frontend tests failed - check the output above"
    fi
    exit 1
fi
