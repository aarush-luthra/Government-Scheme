import requests
import json
import time
import sqlite3
import os
import sys

# Add parent directory to path so we can import backend modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import create_user, get_user_by_email, get_db_connection

BASE_URL = "http://localhost:8000/chat"
TEST_EMAIL = "test_farmer_auto@example.com"

# Profile: Male, 30, Haryana, Farmer, Income 50k
TEST_PROFILE = {
    "email": TEST_EMAIL,
    "password": "password123",
    "name": "Test Farmer",
    "gender": "Male",
    "age": 30,
    "state": "Haryana",
    "area": "Rural",
    "category": "General",
    "employment_status": "Farmer", # Explicitly set to Farmer for PM Kisan test
    "annual_income": 50000,
    "is_govt_employee": False
}

TEST_CASES = [
    {
        "type": "Discovery Mode (Eligible Only)",
        "query": "Show me schemes I am eligible for",
        "expected_snippet": "Eligible ✅",
        "unexpected_snippet": "Not Eligible ⛔" # Strict check: Ineligible schemes should be HIDDEN
    },
    {
        "type": "General Inquiry (No Strict Filter)",
        "query": "Tell me about schemes for farmers in general",
        "expected_snippet": "PM Kisan", # Should find relevant schemes
        "unexpected_snippet": "I couldn't find schemes purely matching your profile" # Should NOT block results due to profile mismatch
    },
    {
        "type": "Specific Scheme application",
        "query": "How to apply for PM Kisan?",
        "expected_snippet": "Visit official website",
        "unexpected_snippet": "Status: Not Eligible" # Should focus on application steps
    },
    {
        "type": "State Mismatch Handling",
        "query": "Tell me about Banglar Awaas Yojana",
        "expected_snippet": "Note: Based on your profile", # Expecting a warning about ineligibility
        "unexpected_snippet": "Status: Eligible ✅"
    },
    {
        "type": "Profile Mismatch (Gender)",
        "query": "Am I eligible for Maternity Benefit?",
        "expected_snippet": "Not Eligible ⛔", 
        "unexpected_snippet": "Eligible ✅" 
    }
]

def setup_user():
    print(f"Creating/Resetting test user: {TEST_EMAIL}")
    # Delete if exists
    clean_user()
    
    # Create
    user = create_user(
        email=TEST_PROFILE["email"],
        password=TEST_PROFILE["password"],
        name=TEST_PROFILE["name"],
        gender=TEST_PROFILE["gender"],
        age=TEST_PROFILE["age"],
        state=TEST_PROFILE["state"],
        area=TEST_PROFILE["area"],
        category=TEST_PROFILE["category"],
        employment_status=TEST_PROFILE["employment_status"],
        annual_income=TEST_PROFILE["annual_income"],
        is_govt_employee=TEST_PROFILE["is_govt_employee"]
    )
    if user:
        print(f"User created with ID: {user['user_id']}")
        return user['user_id']
    else:
        print("Failed to create user.")
        return None

def clean_user():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE email = ?", (TEST_EMAIL,))
    conn.commit()
    conn.close()

def run_tests(user_id):
    results = []
    print(f"Running {len(TEST_CASES)} tests for Signed-In User...\n")
    
    for i, test in enumerate(TEST_CASES):
        print(f"[{i+1}/{len(TEST_CASES)}] Testing '{test['query']}' ({test['type']})...")
        payload = {
            "message": test['query'],
            "user_id": user_id
        }
        
        try:
            start_time = time.time()
            response = requests.post(BASE_URL, json=payload)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                reply = data.get("reply", "")
                
                status = "PASS"
                notes = ""
                
                # Validation
                if test.get("expected_snippet") and test["expected_snippet"] not in reply:
                    status = "FAIL"
                    notes = f"Expected '{test['expected_snippet']}' not found."
                
                if test.get("unexpected_snippet") and test["unexpected_snippet"] in reply:
                    status = "FAIL"
                    notes += f" Found forbidden '{test['unexpected_snippet']}'."

                results.append({
                    "query": test['query'],
                    "type": test['type'],
                    "reply_snippet": reply[:200] + "...",
                    "full_reply": reply,
                    "status": status,
                    "notes": notes,
                    "duration": f"{duration:.2f}s"
                })
            else:
                results.append({"query": test['query'], "error": f"HTTP {response.status_code}"})
                
        except Exception as e:
            results.append({"query": test['query'], "error": str(e)})
        
        time.sleep(1)

    # Save results
    with open("signed_in_test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print("\nSingle-turn Tests Completed.")

def run_conversation_test(user_id):
    print("\nRunning Conversational Flow Test (PM Kisan Land Check)...")
    
    # Turn 1
    q1 = "Am I eligible for PM Kisan?"
    print(f"User: {q1}")
    r1 = requests.post(BASE_URL, json={"message": q1, "user_id": user_id}).json().get("reply", "")
    print(f"Bot: {r1[:100]}...")
    
    # Turn 2
    q2 = "I have 2 hectares of cultivable land"
    print(f"User: {q2}")
    r2 = requests.post(BASE_URL, json={"message": q2, "user_id": user_id}).json().get("reply", "")
    print(f"Bot: {r2[:100]}...")
    
    if "Eligible" in r2 and "Status" in r2:
        print("PASS: Bot updated status after getting land info.")
        return True
    else:
        print("FAIL: Bot did not update status.")
        print(f"Full Reply 2: {r2}")
        return False

if __name__ == "__main__":
    try:
        uid = setup_user()
        if uid:
            run_tests(uid)
            run_conversation_test(uid)
    finally:
        clean_user()
        print("Test user cleaned up.")
