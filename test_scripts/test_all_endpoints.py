import requests
import json

def test_endpoint(method, url, data=None, description=""):
    """Test an API endpoint and print results."""
    print(f"\n=== {description} ===")
    print(f"{method} {url}")
    
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data, headers={"Content-Type": "application/json"})
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Exception: {e}")

# Test all endpoints
if __name__ == "__main__":
    base_url = "http://localhost:8000"
    
    # Health check
    test_endpoint("GET", f"{base_url}/health", description="Health Check")
    
    # API health
    test_endpoint("GET", f"{base_url}/api/v1/health", description="API Health")
    
    # List cases
    test_endpoint("GET", f"{base_url}/api/v1/cases", description="List Cases")
    
    # List rubrics
    test_endpoint("GET", f"{base_url}/api/v1/rubrics", description="List Rubrics")
    
    # Submit grading
    grading_data = {
        "rubric_id": "tcga_ovarian_cancer",
        "case_id": "case-001",
        "user_id": "student-123",
        "student_response": "There is a complex bilateral adnexal mass with mixed solid and cystic components. Trace ascites is present. Multiple soft tissue peritoneal implants are noted along the paracolic gutters and in the left upper quadrant adjacent to the spleen. These findings are suggestive of primary ovarian carcinoma with peritoneal spread.",
        "additional_context": "Student is a radiology resident in their third year."
    }
    
    response = requests.post(
        f"{base_url}/api/v1/grading/submit",
        json=grading_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"\n=== Submit Grading ===")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        session_id = result.get("session_id")
        print(f"Session ID: {session_id}")
        print(f"Response: {json.dumps(result, indent=2)}")
        
        # Test session status
        if session_id:
            test_endpoint("GET", f"{base_url}/api/v1/grading/session/{session_id}", description="Session Status")
            
            # Test grading result
            test_endpoint("GET", f"{base_url}/api/v1/grading/result/{session_id}", description="Grading Result")
    else:
        print(f"Error: {response.text}")
    
    # Test statistics
    test_endpoint("GET", f"{base_url}/api/v1/grading/statistics", description="Grading Statistics") 