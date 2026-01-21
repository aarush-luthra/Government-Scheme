
import sys
import os
import time
import json
import statistics

# Add project root to path
sys.path.append(os.getcwd())

from backend.nlp.indicbart import IndicBartTranslator

DATA_DIR = os.path.join(os.getcwd(), "tests", "data")
os.makedirs(DATA_DIR, exist_ok=True)

def test_translation_metrics():
    print("Loading Translator...")
    start_load = time.time()
    translator = IndicBartTranslator()
    load_time = time.time() - start_load
    
    test_sentences = [
        "Government schemes help citizens.",
        "Pradhan Mantri Awas Yojana provides housing for all.",
        "What are the eligibility criteria for this scholarship?",
        "I am a farmer living in a rural area.",
        "Please tell me about pension schemes for senior citizens."
    ]
    
    # 1. Single Sentence Latency
    latencies = []
    print("\n--- Single Sentence Latency ---")
    translator.translate("Test", target_lang="hi_IN") # Warmup
    
    for text in test_sentences:
        start = time.time()
        translator.translate(text, target_lang="hi_IN")
        dur = time.time() - start
        latencies.append(dur)
        
    avg_latency = statistics.mean(latencies)
    
    # 2. Batch Throughput
    print("\n--- Batch Throughput ---")
    batch_input = test_sentences * 4 
    start_batch = time.time()
    translator.batch_translate(batch_input, target_lang="hi_IN")
    batch_dur = time.time() - start_batch
    throughput = len(batch_input) / batch_dur
    
    metrics = {
        "model_load_time": load_time,
        "avg_single_latency": avg_latency,
        "single_latencies": latencies,
        "batch_throughput": throughput,
        "batch_size": len(batch_input),
        "batch_time": batch_dur
    }

    output_file = os.path.join(DATA_DIR, "translation_metrics.json")
    with open(output_file, "w") as f:
        json.dump(metrics, f, indent=2)
        
    print(f"\nData saved to {output_file}")

if __name__ == "__main__":
    test_translation_metrics()
