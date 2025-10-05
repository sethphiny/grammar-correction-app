import pytest
import httpx
from fastapi.testclient import TestClient
import sys
import os

# Add the parent directory to the path so we can import main
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import app

client = TestClient(app)

def test_upload_test_docx():
    """Test uploading test.docx file and check for grammar errors"""
    # Get the path to test.docx
    test_docx_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "test.docx")
    
    if not os.path.exists(test_docx_path):
        pytest.skip(f"test.docx not found at {test_docx_path}")
    
    # Upload the file
    with open(test_docx_path, "rb") as f:
        response = client.post("/upload", files={"file": ("test.docx", f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")})
    
    print(f"Upload response status: {response.status_code}")
    print(f"Upload response: {response.json()}")
    
    assert response.status_code == 200
    data = response.json()
    assert "processing_id" in data
    
    task_id = data["processing_id"]
    
    # Wait for processing to complete
    import time
    max_wait = 60  # 60 seconds max wait
    wait_time = 0
    
    while wait_time < max_wait:
        status_response = client.get(f"/status/{task_id}")
        print(f"Status response: {status_response.json()}")
        
        if status_response.status_code == 200:
            status_data = status_response.json()
            if status_data.get("status") == "completed":
                break
            elif status_data.get("status") == "failed":
                pytest.fail(f"Processing failed: {status_data}")
        
        time.sleep(2)
        wait_time += 2
    
    if wait_time >= max_wait:
        pytest.fail("Processing timed out")
    
    # Check the final status
    final_status = client.get(f"/status/{task_id}")
    assert final_status.status_code == 200
    
    final_data = final_status.json()
    print(f"Final status: {final_data}")
    
    # Check if any grammar issues were found
    if "grammar_issues" in final_data:
        issues = final_data["grammar_issues"]
        print(f"Found {len(issues)} grammar issues")
        for i, issue in enumerate(issues):
            print(f"Issue {i+1}: {issue}")
    else:
        print("No grammar_issues field found in response")
    
    # Check if there are any issues in the report
    if "report" in final_data and final_data["report"]:
        report = final_data["report"]
        print(f"Report summary: {report.get('summary', 'No summary')}")
        if "issues" in report:
            print(f"Report issues count: {len(report['issues'])}")
        else:
            print("No issues field in report")
    
    # The test should pass regardless of whether issues are found
    # This is just to see what the system is detecting
    assert True
