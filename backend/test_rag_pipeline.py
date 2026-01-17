import requests
import json
import sys

BASE_URL = "http://127.0.0.1:8000"

def test_health():
    print("\n--- Testing Health Endpoint ---")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")

def test_chat_general():
    print("\n--- Testing General Chat ---")
    payload = {
        "message": "What are some schemes for farmers?",
        "source_lang": "en_XX",
        "target_lang": "en_XX"
    }
    try:
        response = requests.post(f"{BASE_URL}/chat", json=payload)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Reply: {response.json()['reply'][:200]}...")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

def test_chat_profile():
    print("\n--- Testing Profile-Based Chat ---")
    payload = {
        "message": "What schemes am I eligible for?",
        "source_lang": "en_XX",
        "target_lang": "en_XX",
        "user_profile": {
            "age": 20,
            "gender": "female",
            "state": "Maharashtra",
            "category": "SC",
            "is_student": True,
            "annual_income": 100000
        }
    }
    try:
        response = requests.post(f"{BASE_URL}/chat", json=payload)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Reply: {response.json()['reply'][:500]}...")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_health()
    test_chat_general()
    test_chat_profile()
