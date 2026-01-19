"""
FAISS-based Vector Store - Compatible with Python 3.14
"""
import faiss
import numpy as np
import pickle
import os
from typing import List, Dict, Any
from backend.config.settings import VECTOR_DB_DIR


class VectorStore:
    """
    FAISS-based vector store for government schemes.
    Stores embeddings and documents separately for efficient retrieval.
    """
    
    def __init__(self, collection_name="government_schemes"):
        self.collection_name = collection_name
        self.index_path = os.path.join(VECTOR_DB_DIR, f"{collection_name}.faiss")
        self.docs_path = os.path.join(VECTOR_DB_DIR, f"{collection_name}_docs.pkl")
        
        os.makedirs(VECTOR_DB_DIR, exist_ok=True)
        
        self.index = None
        self.documents = []
        self.metadatas = []
        
        # Try to load existing index
        if os.path.exists(self.index_path) and os.path.exists(self.docs_path):
            self._load()

    def _load(self):
        """Load existing index and documents."""
        try:
            self.index = faiss.read_index(self.index_path)
            with open(self.docs_path, 'rb') as f:
                data = pickle.load(f)
                self.documents = data['documents']
                self.metadatas = data['metadatas']
            print(f"[INFO] Loaded existing index with {len(self.documents)} documents")
        except Exception as e:
            print(f"[WARN] Could not load existing index: {e}")
            self.index = None
            self.documents = []
            self.metadatas = []

    def _save(self):
        """Save index and documents to disk."""
        faiss.write_index(self.index, self.index_path)
        with open(self.docs_path, 'wb') as f:
            pickle.dump({
                'documents': self.documents,
                'metadatas': self.metadatas
            }, f)
        print(f"[INFO] Saved index with {len(self.documents)} documents")

    def clear(self):
        """Clear the existing index and documents."""
        self.index = None
        self.documents = []
        self.metadatas = []
        # Remove existing files
        if os.path.exists(self.index_path):
            os.remove(self.index_path)
        if os.path.exists(self.docs_path):
            os.remove(self.docs_path)
        print("[INFO] Cleared existing vector store")

    def add_documents(self, documents: List, embeddings: List, clear_existing: bool = True):
        """Add documents with embeddings to the vector store.
        
        Args:
            documents: List of Document objects
            embeddings: List of embedding vectors
            clear_existing: If True, clears existing index before adding (default: True)
        """
        # Clear existing index if requested (prevents duplicates on re-ingestion)
        if clear_existing:
            self.clear()
        
        # Convert embeddings to numpy array
        embeddings_np = np.array(embeddings, dtype=np.float32)
        
        # Create new index (L2 distance)
        dimension = embeddings_np.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.documents = []
        self.metadatas = []
        
        # Add embeddings to index
        self.index.add(embeddings_np)
        
        # Store documents and metadata
        for doc in documents:
            self.documents.append(doc.page_content)
            # Clean metadata - remove None values
            clean_meta = {k: v for k, v in doc.metadata.items() if v is not None}
            self.metadatas.append(clean_meta)
        
        # Save to disk
        self._save()
        print(f"[INFO] Added {len(documents)} documents to vector store")

    def search(self, query_embedding: List[float], k: int = 4) -> List[Dict]:
        """Search for similar documents by embedding."""
        if self.index is None or self.index.ntotal == 0:
            return []
        
        # Convert to numpy
        query_np = np.array([query_embedding], dtype=np.float32)
        
        # Search
        distances, indices = self.index.search(query_np, min(k, self.index.ntotal))
        
        # Build results
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.documents):
                results.append({
                    'content': self.documents[idx],
                    'metadata': self.metadatas[idx],
                    'distance': float(distances[0][i])
                })
        
        return results
    
    def clear(self):
        """Clear the index and remove files."""
        self.index = None
        self.documents = []
        self.metadatas = []
        
        if os.path.exists(self.index_path):
            os.remove(self.index_path)
        if os.path.exists(self.docs_path):
            os.remove(self.docs_path)
        print(f"[INFO] Cleared vector store")
