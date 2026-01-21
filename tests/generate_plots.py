
import sys
import os
import json
import matplotlib.pyplot as plt
import numpy as np

# Add project root to path
sys.path.append(os.getcwd())

DATA_DIR = os.path.join(os.getcwd(), "tests", "data")
PLOTS_DIR = os.path.join(os.getcwd(), "tests", "plots")
os.makedirs(PLOTS_DIR, exist_ok=True)

def generate_retrieval_plot():
    json_path = os.path.join(DATA_DIR, "retrieval_metrics.json")
    if not os.path.exists(json_path):
        print(f"File not found: {json_path}")
        return

    with open(json_path, "r") as f:
        data = json.load(f)

    profiles = [p["name"].replace(" Profile", "") for p in data["profiles"]]
    latencies = [p["latency"] for p in data["profiles"]]
    precisions = [p["precision"] * 100 for p in data["profiles"]]

    fig, ax1 = plt.subplots(figsize=(10, 6))

    color = 'tab:blue'
    ax1.set_xlabel('User Profile')
    ax1.set_ylabel('Latency (seconds)', color=color)
    bars = ax1.bar(profiles, latencies, color=color, alpha=0.6, label='Latency')
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.set_ylim(0, max(latencies) * 1.2)

    # Add value labels for latency
    for bar in bars:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                 f'{height:.2f}s',
                 ha='center', va='bottom')

    ax2 = ax1.twinx()  
    color = 'tab:green'
    ax2.set_ylabel('Precision (%)', color=color)  
    line = ax2.plot(profiles, precisions, color=color, marker='o', linewidth=2, label='Precision')
    ax2.tick_params(axis='y', labelcolor=color)
    ax2.set_ylim(0, 110)

    # Add value labels for precision
    for i, txt in enumerate(precisions):
        ax2.annotate(f"{txt:.0f}%", (profiles[i], precisions[i]), 
                     textcoords="offset points", xytext=(0,10), ha='center')

    plt.title('Retrieval Performance by Profile Type')
    fig.tight_layout()  
    
    out_path = os.path.join(PLOTS_DIR, "retrieval_performance.png")
    plt.savefig(out_path)
    print(f"Saved plot: {out_path}")
    plt.close()

def generate_translation_plot():
    json_path = os.path.join(DATA_DIR, "translation_metrics.json")
    if not os.path.exists(json_path):
        print(f"File not found: {json_path}")
        return

    with open(json_path, "r") as f:
        data = json.load(f)

    # Plot 1: Latency Distribution
    latencies = data["single_latencies"]
    
    plt.figure(figsize=(8, 5))
    plt.hist(latencies, bins=5, color='skyblue', edgecolor='black')
    plt.title('Translation Latency Distribution (Single Sentence)')
    plt.xlabel('Latency (seconds)')
    plt.ylabel('Frequency')
    plt.axvline(data["avg_single_latency"], color='red', linestyle='dashed', linewidth=1, label=f'Avg: {data["avg_single_latency"]:.2f}s')
    plt.legend()
    
    out_path = os.path.join(PLOTS_DIR, "translation_latency_dist.png")
    plt.savefig(out_path)
    print(f"Saved plot: {out_path}")
    plt.close()

    # Plot 2: Throughput text/visual
    # Since its a single value, maybe a small bar chart comparing Single vs Batch
    
    single_throughput = 1 / data["avg_single_latency"]
    batch_throughput = data["batch_throughput"]
    
    modes = ['Single Request', 'Batch Processing']
    values = [single_throughput, batch_throughput]
    
    plt.figure(figsize=(8, 5))
    bars = plt.bar(modes, values, color=['orange', 'purple'])
    plt.title('Translation Throughput Comparison')
    plt.ylabel('Sentences per Second (FPS)')
    
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                 f'{height:.2f}',
                 ha='center', va='bottom')
                 
    out_path = os.path.join(PLOTS_DIR, "translation_throughput.png")
    plt.savefig(out_path)
    print(f"Saved plot: {out_path}")
    plt.close()

if __name__ == "__main__":
    generate_retrieval_plot()
    generate_translation_plot()
