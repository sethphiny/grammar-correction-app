#!/bin/bash

# Grammar Correction App - Test Frontend
# This script runs tests for the React frontend

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

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================${NC}"
}

# Check if we're in the right directory
if [ ! -f "frontend/package.json" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

print_header "🧪 Testing Grammar Correction Frontend"

cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    print_error "Dependencies not installed. Please run './scripts/dev-setup.sh' first"
    exit 1
fi

# Create test directory if it doesn't exist
mkdir -p src/__tests__

# Create a simple test file if it doesn't exist
if [ ! -f "src/__tests__/App.test.tsx" ]; then
    print_status "Creating basic App test file..."
    cat > src/__tests__/App.test.tsx << 'EOF'
import React from 'react';
import { render, screen } from '@testing-library/react';
import App from '../App';

// Mock the API module
jest.mock('../services/api', () => ({
  healthCheck: jest.fn().mockResolvedValue({ status: 'healthy', timestamp: '2023-01-01T00:00:00' }),
  uploadDocument: jest.fn(),
  getProcessingStatus: jest.fn(),
  downloadReport: jest.fn(),
  cleanupProcessing: jest.fn(),
}));

describe('App Component', () => {
  test('renders the main heading', () => {
    render(<App />);
    const heading = screen.getByText(/Grammar Correction App/i);
    expect(heading).toBeInTheDocument();
  });

  test('renders file upload component when no status', () => {
    render(<App />);
    const uploadText = screen.getByText(/Upload a Word document/i);
    expect(uploadText).toBeInTheDocument();
  });
});
EOF
    print_success "Created App.test.tsx ✓"
fi

# Create setupTests.ts if it doesn't exist
if [ ! -f "src/setupTests.ts" ]; then
    print_status "Creating setupTests.ts..."
    cat > src/setupTests.ts << 'EOF'
// jest-dom adds custom jest matchers for asserting on DOM nodes.
// allows you to do things like:
// expect(element).toHaveTextContent(/react/i)
// learn more: https://github.com/testing-library/jest-dom
import '@testing-library/jest-dom';
EOF
    print_success "Created setupTests.ts ✓"
fi

# Run the tests
print_status "Running frontend tests..."
echo ""

if npm test -- --watchAll=false --verbose; then
    print_success "All frontend tests passed! ✓"
else
    print_error "Some frontend tests failed!"
    exit 1
fi

echo ""
print_header "🔍 Manual Frontend Testing"

print_status "You can also test the frontend manually:"
echo ""
echo "1. Start the frontend server:"
echo "   ./scripts/start-frontend.sh"
echo ""
echo "2. Or start both frontend and backend:"
echo "   ./scripts/start-dev.sh"
echo ""
echo "3. Open your browser to:"
echo "   http://localhost:3000"
echo ""
echo "4. Test the following features:"
echo "   • File upload (drag & drop or click to select)"
echo "   • Format selection (DOCX/PDF)"
echo "   • Custom filename input"
echo "   • Progress tracking during processing"
echo "   • Issues preview and download"
echo ""

print_status "For testing with real files, you can:"
echo ""
echo "1. Create a test Word document with some grammar issues"
echo "2. Upload it through the web interface"
echo "3. Check the generated report"
echo ""

print_success "Frontend testing complete! ✓"
