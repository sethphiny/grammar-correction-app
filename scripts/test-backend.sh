#!/bin/bash

# Grammar Correction App - Test Backend
# This script runs tests for the backend API

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
if [ ! -f "backend/main.py" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

print_header "🧪 Testing Grammar Correction Backend"

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
export JAVA_HOME="/usr/local/opt/openjdk@17"
export PATH="/usr/local/opt/openjdk@17/bin:$PATH"

# Install test dependencies if not already installed
print_status "Installing test dependencies..."
pip install pytest pytest-asyncio httpx

# Create test directory if it doesn't exist
mkdir -p tests

# Create a simple test file if it doesn't exist
if [ ! -f "tests/test_api.py" ]; then
    print_status "Creating basic API test file..."
    cat > tests/test_api.py << 'EOF'
import pytest
import httpx
from fastapi.testclient import TestClient
import sys
import os

# Add the parent directory to the path so we can import main
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import app

client = TestClient(app)

def test_health_endpoint():
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "healthy"

def test_root_endpoint():
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data

def test_upload_endpoint_without_file():
    """Test upload endpoint without file (should fail)"""
    response = client.post("/upload")
    assert response.status_code == 422  # Validation error

def test_status_endpoint_not_found():
    """Test status endpoint with non-existent ID"""
    response = client.get("/status/non-existent-id")
    assert response.status_code == 404

def test_download_endpoint_not_found():
    """Test download endpoint with non-existent ID"""
    response = client.get("/download/non-existent-id")
    assert response.status_code == 404

def test_cleanup_endpoint_not_found():
    """Test cleanup endpoint with non-existent ID"""
    response = client.delete("/cleanup/non-existent-id")
    assert response.status_code == 200  # Should succeed even if ID doesn't exist
EOF
    print_success "Created test_api.py ✓"
fi

# Run the tests
print_status "Running backend tests..."
echo ""

if python -m pytest tests/ -v --tb=short; then
    print_success "All backend tests passed! ✓"
else
    print_error "Some backend tests failed!"
    exit 1
fi

echo ""
print_header "🔍 Testing with test.docx File"

# Check if test.docx exists
if [ ! -f "../test.docx" ]; then
    print_error "test.docx file not found in project root"
    exit 1
fi

print_status "Testing with test.docx file..."
echo ""

# Start the backend server in background
print_status "Starting backend server..."
python main.py &
SERVER_PID=$!

# Wait for server to start
sleep 3

# Test the API with test.docx
print_status "Uploading test_2.docx for processing..."

# Upload the file and get processing ID
UPLOAD_RESPONSE=$(curl -s -X POST 'http://localhost:8000/upload' \
    -F 'file=@../test_2.docx' \
    -F 'output_format=docx' \
    -F 'custom_filename=corrected_test_2')

echo "Upload response: $UPLOAD_RESPONSE"

# Extract processing ID from response
PROCESSING_ID=$(echo $UPLOAD_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['processing_id'])")

if [ -z "$PROCESSING_ID" ]; then
    print_error "Failed to get processing ID"
    kill $SERVER_PID 2>/dev/null
    exit 1
fi

print_success "Processing ID: $PROCESSING_ID"

# Monitor processing status
print_status "Monitoring processing status..."
while true; do
    STATUS_RESPONSE=$(curl -s "http://localhost:8000/status/$PROCESSING_ID")
    STATUS=$(echo $STATUS_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['status'])")
    PROGRESS=$(echo $STATUS_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['progress'])")
    MESSAGE=$(echo $STATUS_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['message'])")
    
    echo "Status: $STATUS ($PROGRESS%) - $MESSAGE"
    
    if [ "$STATUS" = "completed" ]; then
        print_success "Processing completed!"
        break
    elif [ "$STATUS" = "error" ]; then
        print_error "Processing failed: $MESSAGE"
        kill $SERVER_PID 2>/dev/null
        exit 1
    fi
    
    sleep 2
done

# Download the corrected file
print_status "Downloading corrected file..."
curl -s "http://localhost:8000/download/$PROCESSING_ID" -o "../corrected_test.docx"

if [ -f "../corrected_test.docx" ]; then
    print_success "Corrected file saved as: corrected_test.docx"
    print_status "File size: $(ls -lh ../corrected_test.docx | awk '{print $5}')"
else
    print_error "Failed to download corrected file"
fi

# Clean up
print_status "Cleaning up..."
curl -s -X DELETE "http://localhost:8000/cleanup/$PROCESSING_ID" > /dev/null

# Stop the server
kill $SERVER_PID 2>/dev/null
wait $SERVER_PID 2>/dev/null

echo ""
print_header "📋 Manual API Testing Guide"

print_status "You can also test the API manually:"
echo ""
echo "1. Start the backend server:"
echo "   ./scripts/start-backend.sh"
echo ""
echo "2. Test the health endpoint:"
echo "   curl http://localhost:8000/health"
echo ""
echo "3. Test file upload:"
echo "   curl -X POST 'http://localhost:8000/upload' \\"
echo "        -F 'file=@test.docx' \\"
echo "        -F 'output_format=docx' \\"
echo "        -F 'custom_filename=my_corrected_file'"
echo ""
echo "4. View API documentation:"
echo "   http://localhost:8000/docs"
echo ""

print_success "Backend testing complete! ✓"
