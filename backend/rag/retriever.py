"""
Vector Store Retriever - FAISS-based retrieval with Eligibility Filtering.
"""
from backend.rag.embeddings import EmbeddingGenerator
from backend.rag.vector_store import VectorStore
from backend.rag.scheme_matcher import SchemeMatcher  # ✅ Import the matcher
from typing import List, Dict, Optional
from langchain_core.documents import Document


class VectorStoreRetriever:
    """
    Retriever for searching government schemes.
    Includes re-ranking to enforce State/Disability/Income/Age hard filters.
    """
    
    def __init__(self):
        self.embedder = EmbeddingGenerator()
        self.vectorstore = VectorStore()
        print("[INFO] VectorStoreRetriever initialized")

    def search(self, query: str, k: int = 4) -> List[Document]:
        """Basic similarity search."""
        query_embedding = self.embedder.embed_query(query)
        results = self.vectorstore.search(query_embedding, k=k)
        
        documents = []
        for result in results:
            metadata = result['metadata'].copy()
            metadata['distance'] = result['distance']
            
            doc = Document(
                page_content=result['content'],
                metadata=metadata
            )
            documents.append(doc)
        
        return documents
    
    def search_multi_query(self, queries: List[str], k_per_query: int = 2) -> List[Document]:
        """Search using multiple queries and deduplicate results."""
        all_docs = []
        seen_content = set()
        
        for query in queries:
            docs = self.search(query, k=k_per_query)
            for doc in docs:
                content_hash = hash(doc.page_content[:200])
                if content_hash not in seen_content:
                    seen_content.add(content_hash)
                    all_docs.append(doc)
        
        return all_docs
    
    def search_by_profile(self, user_profile: Dict, k: int = 5) -> List[Document]:
        """
        Search for schemes based on user profile AND filter by eligibility.
        
        Process:
        1. Generate Queries (SchemeMatcher)
        2. Vector Search (FAISS) -> High Recall
        3. Re-Rank & Filter (SchemeMatcher) -> High Precision
        """
        # 1. Generate search queries from profile
        queries = SchemeMatcher.extract_search_queries(user_profile)
        
        # 2. Run multi-query search (Fetch 3x candidates to allow for Hard Filtering)
        raw_docs = self.search_multi_query(queries, k_per_query=3)
        
        # Fallback: If not enough results, add a general search
        if len(raw_docs) < k:
            general_docs = self.search("government scheme eligibility benefits", k=4)
            for doc in general_docs:
                content_hash = hash(doc.page_content[:200])
                if content_hash not in {hash(d.page_content[:200]) for d in raw_docs}:
                    raw_docs.append(doc)
        
        # 3. RE-RANKING & FILTERING (The Logic Step)
        # This applies your State, Disability, Income, Age, Category rules
        ranked_results = SchemeMatcher.rank_schemes(user_profile, raw_docs)
        
        final_docs = []
        print(f"\n[RETRIEVER] Re-ranking {len(raw_docs)} schemes for user profile...")
        
        for doc, confidence, reasons in ranked_results[:k]:
            # Store logic results in metadata so LLM can explain "Why You're Eligible"
            doc.metadata['match_confidence'] = confidence
            doc.metadata['eligibility_reasons'] = "\n".join(reasons)
            
            final_docs.append(doc)
            print(f"   -> Selected: {doc.metadata.get('scheme_name')} (Conf: {confidence:.2f})")
            
        return final_docs