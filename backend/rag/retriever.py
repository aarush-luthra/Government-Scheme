"""
Vector Store Retriever - FAISS-based retrieval for government schemes.
"""
from backend.rag.embeddings import EmbeddingGenerator
from backend.rag.vector_store import VectorStore
from typing import List, Dict, Optional
from langchain_core.documents import Document


class VectorStoreRetriever:
    """
    Retriever for searching government schemes in the FAISS vector store.
    Supports both general similarity search and profile-based filtering.
    """
    
    def __init__(self):
        self.embedder = EmbeddingGenerator()
        self.vectorstore = VectorStore()
        print(" VectorStoreRetriever initialized")

    def search(self, query: str, k: int = 4) -> List[Document]:
        """Basic similarity search."""
        # Get query embedding
        query_embedding = self.embedder.embed_query(query)
        
        # Search vector store
        results = self.vectorstore.search(query_embedding, k=k)
        
        # Convert to Document objects
        documents = []
        for result in results:
            # Add distance to metadata so it's preserved
            metadata = result['metadata'].copy()
            metadata['distance'] = result['distance']
            
            doc = Document(
                page_content=result['content'],
                metadata=metadata
            )
            documents.append(doc)
        
        # Log retrieved documents
        print(f"\n[RETRIEVER] Retrieved {len(documents)} documents for query: '{query}'")
        for i, doc in enumerate(documents):
            # Fallback to 'title' if 'scheme_name' is missing
            scheme_name = doc.metadata.get('scheme_name') or doc.metadata.get('title') or 'Unknown'
            print(f"   {i+1}. {scheme_name} (Score: {doc.metadata.get('distance', 0):.4f})")
            
        return documents
    
    def search_with_filter(self, query: str, filter_dict: Dict, k: int = 4) -> List[Document]:
        """
        Search with metadata filtering.
        Note: FAISS doesn't support native filtering, so we filter post-search.
        """
        # Get more results than needed to allow for filtering
        docs = self.search(query, k=k * 3)
        
        # Filter by metadata
        filtered = []
        for doc in docs:
            match = True
            for key, value in filter_dict.items():
                if doc.metadata.get(key) != value:
                    match = False
                    break
            if match:
                filtered.append(doc)
        
        return filtered[:k]
    
    def search_eligibility(self, query: str, k: int = 6) -> List[Document]:
        """
        Search specifically for eligibility-type documents.
        """
        return self.search_with_filter(
            query,
            filter_dict={"chunk_type": "eligibility"},
            k=k
        )
    
    def search_multi_query(self, queries: List[str], k_per_query: int = 2) -> List[Document]:
        """
        Search using multiple queries and deduplicate results.
        Useful for profile-based search with multiple characteristics.
        """
        all_docs = []
        seen_content = set()
        
        for query in queries:
            docs = self.search(query, k=k_per_query)
            for doc in docs:
                # Deduplicate by content hash
                content_hash = hash(doc.page_content[:200])
                if content_hash not in seen_content:
                    seen_content.add(content_hash)
                    all_docs.append(doc)
        
        return all_docs
    
    def search_by_profile(self, user_profile: Dict, k: int = 8) -> List[Document]:
        """
        Search for schemes based on user profile characteristics.
        Generates multiple queries based on profile and aggregates results.
        """
        from backend.rag.scheme_matcher import SchemeMatcher
        
        # Generate search queries from profile
        queries = SchemeMatcher.extract_search_queries(user_profile)
        
        # Run multi-query search
        docs = self.search_multi_query(queries, k_per_query=3)
        
        # If not enough results, add a general search
        if len(docs) < k:
            general_docs = self.search("government scheme eligibility benefits", k=4)
            for doc in general_docs:
                content_hash = hash(doc.page_content[:200])
                if content_hash not in {hash(d.page_content[:200]) for d in docs}:
                    docs.append(doc)
        
        return docs[:k * 2]  # Return more docs for ranking later
