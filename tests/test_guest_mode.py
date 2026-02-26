import requests
import json
import time

BASE_URL = "http://localhost:8000/chat"
USER_ID = None  # Guest User

TEST_CASES = [
    {"type": "Greeting", "query": "Hello"},
    {"type": "General Chat", "query": "Who are you?"},
    {"type": "Off-Topic", "query": "What is the capital of France?"},
    {"type": "Off-Topic", "query": "What time is it?"},
    {"type": "Topic Search", "query": "Schemes for farmers"},
    {"type": "Topic Search", "query": "Scholarships for students"},
    {"type": "Specific - Benefits", "query": "Benefits of PM Kisan"},
    {"type": "Specific - Eligibility", "query": "Eligibility for Atal Pension Yojana"},
    {"type": "Specific - Application", "query": "How to apply for Mudra Loan"},
    {"type": "Contextual", "query": "I am a 22 year old student from Delhi, suggest schemes"},
    {"type": "Contextual", "query": "I am a farmer with 2 hectares of land in Maharashtra"}
]

def run_tests():
    results = []
    print(f"Running {len(TEST_CASES)} strict tests for Guest Mode...\n")
    
    for i, test in enumerate(TEST_CASES):
        print(f"[{i+1}/{len(TEST_CASES)}] Testing '{test['query']}' ({test['type']})...")
        payload = {
            "message": test['query'],
            "user_id": USER_ID
        }
        
        try:
            start_time = time.time()
            response = requests.post(BASE_URL, json=payload)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                reply = data.get("reply", "")
                
                # Basic Validation Logic
                status = "PASS"
                notes = ""
                
                if test['type'] == "Off-Topic" and "scheme" not in reply.lower() and "sorry" not in reply.lower() and "help" not in reply.lower():
                     if "capital" in test['query']: # It might actually answer general knowledge now? No, strictly scheme bot.
                         pass
                
                if test['type'] == "Specific - Eligibility" and "application" in reply.lower():
                    status = "WARN: Application details found in Eligibility query"
                
                if test['type'] == "Contextual" and "Info Only" in reply and "Likely" not in reply:
                    status = "WARN: Context provided but Status is still Info Only (Check Prompt Logic)"

                results.append({
                    "query": test['query'],
                    "type": test['type'],
                    "reply_snippet": reply[:200] + "...",
                    "full_reply": reply,
                    "status": status,
                    "duration": f"{duration:.2f}s"
                })
            else:
                results.append({"query": test['query'], "error": f"HTTP {response.status_code}"})
                
        except Exception as e:
            results.append({"query": test['query'], "error": str(e)})
        
        # small delay to prevent rate limits if any
        time.sleep(0.5)

    # Save results
    with open("guest_mode_test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print("\nTests Completed. Results saved to guest_mode_test_results.json")

if __name__ == "__main__":
    run_tests()
