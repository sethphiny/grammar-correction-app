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
