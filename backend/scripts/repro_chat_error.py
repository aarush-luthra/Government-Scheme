
import sys
import os
import asyncio
# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app import app
from backend.app import ChatRequest

async def test_chat():
    print("Testing chat endpoint...")
    req = ChatRequest(message="hi", source_lang="en_XX")
    try:
        # We need to simulate the app state or just call the function if possible
        # Since app.py logic is inside a route, we can try to call it via TestClient
        from fastapi.testclient import TestClient
        client = TestClient(app)
        
        response = client.post("/chat", json={
            "message": "hi",
            "source_lang": "en_XX",
            "user_profile": {"age": 25, "gender": "male", "state": "Delhi"}
        })
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
    except Exception as e:
        print(f"CRASHED: {e}")

if __name__ == "__main__":
    asyncio.run(test_chat())
