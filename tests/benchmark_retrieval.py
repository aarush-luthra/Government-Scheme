
import sys
import os
import time
import json
from typing import Dict, List

# Add project root to path
sys.path.append(os.getcwd())

from backend.rag.retriever import VectorStoreRetriever
from backend.rag.scheme_matcher import SchemeMatcher

DATA_DIR = os.path.join(os.getcwd(), "tests", "data")
os.makedirs(DATA_DIR, exist_ok=True)

def test_retrieval_metrics():
    print("Initializing Retriever...")
    retriever = VectorStoreRetriever()

    # Define Test Profiles
    profiles = [
        {
            "name": "Student Profile",
            "data": {"age": 20, "state": "Maharashtra", "is_student": True, "category": "General", "annual_income": 100000},
            "query": "scholarships for college students"
        },
        {
            "name": "Farmer Profile",
            "data": {"age": 45, "state": "Punjab", "employment_status": "Farmer", "category": "OBC", "annual_income": 300000},
            "query": "loans for agriculture"
        },
        {
            "name": "Senior Citizen Profile",
            "data": {"age": 65, "state": "Tamil Nadu", "is_disabled": False, "category": "SC", "annual_income": 50000},
            "query": "pension scheme"
        }
    ]

    metrics = {
        "profiles": [],
        "overall_precision": 0,
        "overall_latency": 0
    }

    total_precision = 0
    total_latency = 0

    print("\n--- Starting Retrieval Benchmark ---")

    for p in profiles:
        print(f"\nTesting: {p['name']}")
        
        start_time = time.time()
        results = retriever.search_by_profile(p['data'], query=p['query'], k=10)
        latency = time.time() - start_time
        total_latency += latency
        
        eligible_count = 0
        for doc in results:
            is_eligible, _, _ = SchemeMatcher.check_eligibility_match(p['data'], doc.metadata)
            if is_eligible:
                eligible_count += 1

        precision = eligible_count / len(results) if results else 0
        total_precision += precision
        
        p_metric = {
            "name": p["name"],
            "latency": latency,
            "precision": precision,
            "docs_retrieved": len(results)
        }
        metrics["profiles"].append(p_metric)
        
        print(f"  Latency: {latency:.4f}s")
        print(f"  Precision: {precision*100:.1f}%")

    metrics["overall_precision"] = (total_precision / len(profiles)) if profiles else 0
    metrics["overall_latency"] = (total_latency / len(profiles)) if profiles else 0

    output_file = os.path.join(DATA_DIR, "retrieval_metrics.json")
    with open(output_file, "w") as f:
        json.dump(metrics, f, indent=2)
    
    print(f"\nData saved to {output_file}")

if __name__ == "__main__":
    test_retrieval_metrics()
