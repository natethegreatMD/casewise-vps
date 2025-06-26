import requests
import json

# Test data for grading submission
test_data = {
    "rubric_id": "tcga_ovarian_cancer",
    "case_id": "case-001",
    "user_id": "student-123",
    "student_response": "There is a complex bilateral adnexal mass with mixed solid and cystic components. Trace ascites is present. Multiple soft tissue peritoneal implants are noted along the paracolic gutters and in the left upper quadrant adjacent to the spleen. These findings are suggestive of primary ovarian carcinoma with peritoneal spread.",
    "additional_context": "Student is a radiology resident in their third year."
}

# Make POST request to grading endpoint
response = requests.post(
    "http://localhost:8000/api/v1/grading/submit",
    json=test_data,
    headers={"Content-Type": "application/json"}
)

print(f"Status Code: {response.status_code}")
print(f"Response: {response.text}") 