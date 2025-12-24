import json
import os
from ingestion.loaders.unified_scheme_loader import UnifiedSchemeLoader
from ingestion.normalizer import normalize_scheme
from ingestion.chunker import chunk_scheme
from rag.embeddings import EmbeddingGenerator
from rag.vector_store import VectorStore
from config.settings import RAW_DATA_DIR


def run_ingestion(limit=None):
    loader = UnifiedSchemeLoader()
    schemes = loader.load_all_schemes(limit)

    os.makedirs(RAW_DATA_DIR, exist_ok=True)
    with open(os.path.join(RAW_DATA_DIR, "schemes_raw.json"), "w") as f:
        json.dump(schemes, f, indent=2)

    normalized = [normalize_scheme(s) for s in schemes]

    documents = []
    for scheme in normalized:
        documents.extend(chunk_scheme(scheme))

    embedder = EmbeddingGenerator()
    embeddings = embedder.embed_texts([d.page_content for d in documents])

    store = VectorStore()
    store.add_documents(documents, embeddings)

    print(f"✓ Ingested {len(schemes)} schemes")
