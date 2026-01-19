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
from backend.rag.scheme_links_loader import load_scheme_links, get_scheme_links
from backend.config.settings import RAW_DATA_DIR


def merge_scheme_links(schemes: list) -> list:
    """
    Merge official_site and apply_link from scheme_links.json into each scheme.
    """
    # Load the links lookup
    links_lookup = load_scheme_links()
    
    merged_count = 0
    for scheme in schemes:
        title = scheme.get("title", "")
        official, apply_link = get_scheme_links(title)
        
        if official:
            scheme["official_site"] = official
            merged_count += 1
        else:
            scheme["official_site"] = ""
        
        if apply_link:
            scheme["apply_link"] = apply_link
        else:
            scheme["apply_link"] = ""
    
    print(f"   Merged links for {merged_count} schemes (out of {len(schemes)})")
    return schemes


def run_ingestion(limit=None):
    """
    Run the full ingestion pipeline:
    1. Load schemes from JSON files in backend/data/schemes_json/
    2. Merge scheme links from scheme_links.json
    3. Normalize to consistent format
    4. Chunk into documents (eligibility-focused)
    5. Generate embeddings
    6. Store in vector database
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
    
    # Merge scheme links from scheme_links.json
    print("\n[INFO] Merging scheme links...")
    schemes = merge_scheme_links(schemes)
    
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
