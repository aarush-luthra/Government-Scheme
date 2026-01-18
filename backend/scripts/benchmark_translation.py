
import time
import sys
import os

# Add parent directory to path so we can import backend modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.nlp.indicbart import IndicBartTranslator

def benchmark():
    print("Initializing translator...")
    translator = IndicBartTranslator()
    
    # Test texts (mixed length)
    texts = [
        "Government Scheme Assistant",
        "Get government benefits",
        "I can help you understand Indian government schemes",
        "What are the benefits of this scheme?",
        "How do I apply for this?",
        "Is there an age limit?",
        "Secure, Simple, Seamless",
        "Fast-track",
        "Explore Schemes",
        "Continue as Guest",
        "New User",
        "Sign In",
        "Your Language",
        "Your State",
        "All India",
        "Schemes Available",
        "AI-Powered Assistance",
        "Supported Languages",
        "Welcome to Government Scheme Assistant",
        "3 free messages remaining"
    ]
    
    print(f"\nStarting benchmark with {len(texts)} sentences...")
    print(f"Target Language: Hindi (hi_IN)")
    
    # Warmup
    print("Warming up...")
    translator.translate("Hello", target_lang="hi_IN")
    
    # Measure
    start_time = time.time()
    results = translator.batch_translate(texts, target_lang="hi_IN")
    end_time = time.time()
    
    duration = end_time - start_time
    avg_per_sentence = duration / len(texts)
    
    print(f"\nResults:")
    print(f"Total Time: {duration:.4f} seconds")
    print(f"Average Time per Sentence: {avg_per_sentence:.4f} seconds")
    print(f"Throughput: {len(texts)/duration:.2f} sentences/second")
    print("-" * 30)

if __name__ == "__main__":
    benchmark()
