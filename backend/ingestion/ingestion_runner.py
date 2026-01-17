"""
Ingestion Runner - Loads government schemes from JSON files and ingests them into the vector store.
"""
import json
import os
import sys

# Add backend to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.ingestion.loaders.json_scheme_loader import JSONSchemeLoader
from backend.ingestion.normalizer import normalize_scheme
from backend.ingestion.chunker import chunk_scheme
from backend.rag.embeddings import EmbeddingGenerator
from backend.rag.vector_store import VectorStore
from backend.config.settings import RAW_DATA_DIR


def run_ingestion(limit=None):
    """
    Run the full ingestion pipeline:
    1. Load schemes from JSON files in backend/data/schemes_json/
    2. Normalize to consistent format
    3. Chunk into documents (eligibility-focused)
    4. Generate embeddings
    5. Store in vector database
    """
    print("=" * 60)
    print("Government Scheme Ingestion Pipeline")
    print("=" * 60)
    
    # Load schemes using the JSON loader
    loader = JSONSchemeLoader()
    schemes = loader.load_all_schemes(limit)
    
    if not schemes:
        print("[ERROR] No schemes loaded. Check data directory.")
        return
    
    # Save raw data for debugging
    os.makedirs(RAW_DATA_DIR, exist_ok=True)
    raw_output = os.path.join(RAW_DATA_DIR, "schemes_raw.json")
    with open(raw_output, "w", encoding="utf-8") as f:
        # Remove eligibility_criteria for JSON serialization (contains None values)
        serializable_schemes = []
        for s in schemes:
            scheme_copy = {k: v for k, v in s.items() if k != "eligibility_criteria"}
            serializable_schemes.append(scheme_copy)
        json.dump(serializable_schemes, f, indent=2, ensure_ascii=False)
    print(f"[INFO] Raw schemes saved to: {raw_output}")
    
    # Normalize schemes
    print("\n[INFO] Normalizing schemes...")
    normalized = [normalize_scheme(s) for s in schemes]
    
    # Chunk into documents
    print("[INFO] Chunking schemes into documents...")
    documents = []
    for scheme in normalized:
        documents.extend(chunk_scheme(scheme))
    print(f"   Created {len(documents)} document chunks")
    
    # Generate embeddings
    print("\n[INFO] Generating embeddings (this may take a while)...")
    embedder = EmbeddingGenerator()
    
    # Process in batches to avoid memory issues
    batch_size = 100
    all_embeddings = []
    for i in range(0, len(documents), batch_size):
        batch = documents[i:i+batch_size]
        batch_texts = [d.page_content for d in batch]
        batch_embeddings = embedder.embed_texts(batch_texts)
        all_embeddings.extend(batch_embeddings)
        print(f"   Processed {min(i+batch_size, len(documents))}/{len(documents)} chunks")
    
    # Store in vector database
    print("\n[INFO] Storing in vector database...")
    store = VectorStore()
    store.add_documents(documents, all_embeddings)
    
    print("\n" + "=" * 60)
    print(f"[SUCCESS] Ingestion complete!")
    print(f"   - Schemes loaded: {len(schemes)}")
    print(f"   - Document chunks: {len(documents)}")
    print("=" * 60)


if __name__ == "__main__":
    run_ingestion()
