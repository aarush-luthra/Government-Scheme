import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import List, Dict, Optional
import os
from backend.config.settings import settings
from backend.rag.embeddings import EmbeddingGenerator


class VectorStoreRetriever:
    """Manage vector store and retrieve relevant documents"""
    
    def __init__(self):
        # Initialize ChromaDB
        self.chroma_client = chromadb.PersistentClient(
            path=settings.CHROMA_PERSIST_DIRECTORY,
            settings=ChromaSettings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Initialize embedding generator
        self.embedding_generator = EmbeddingGenerator()
        
        # Collection name
        self.collection_name = "government_schemes"
        
        # Get or create collection
        try:
            self.collection = self.chroma_client.get_collection(
                name=self.collection_name
            )
            print(f"Loaded existing collection: {self.collection_name}")
        except:
            self.collection = self.chroma_client.create_collection(
                name=self.collection_name,
                metadata={"description": "Government schemes knowledge base"}
            )
            print(f"Created new collection: {self.collection_name}")
    
    def add_documents(
        self,
        documents: List[str],
        metadatas: List[Dict],
        ids: Optional[List[str]] = None
    ) -> None:
        """
        Add documents to the vector store
        
        Args:
            documents: List of text documents to add
            metadatas: List of metadata dictionaries for each document
            ids: Optional list of unique IDs for documents
        """
        if not documents:
            print("No documents to add")
            return
        
        # Generate IDs if not provided
        if ids is None:
            ids = [f"doc_{i}" for i in range(len(documents))]
        
        # Generate embeddings
        print(f"Generating embeddings for {len(documents)} documents...")
        embeddings = self.embedding_generator.generate_embeddings_batch(documents)
        
        # Add to collection in batches
        batch_size = 100
        for i in range(0, len(documents), batch_size):
            end_idx = min(i + batch_size, len(documents))
            
            self.collection.add(
                embeddings=embeddings[i:end_idx],
                documents=documents[i:end_idx],
                metadatas=metadatas[i:end_idx],
                ids=ids[i:end_idx]
            )
            
            print(f"Added batch {i//batch_size + 1}: documents {i+1} to {end_idx}")
        
        print(f"Successfully added {len(documents)} documents to vector store")
    
    def retrieve(
        self,
        query: str,
        top_k: int = None,
        filter_metadata: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Retrieve most relevant documents for a query
        
        Args:
            query: Search query
            top_k: Number of results to return
            filter_metadata: Optional metadata filters
        
        Returns:
            List of relevant documents with metadata and scores
        """
        if top_k is None:
            top_k = settings.TOP_K_RESULTS
        
        # Generate query embedding
        query_embedding = self.embedding_generator.generate_embedding(query)
        
        # Search in vector store
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=filter_metadata
        )
        
        # Format results
        retrieved_docs = []
        
        if results['documents'] and len(results['documents']) > 0:
            for i in range(len(results['documents'][0])):
                doc = {
                    'id': results['ids'][0][i],
                    'content': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'score': 1 - results['distances'][0][i]  # Convert distance to similarity
                }
                retrieved_docs.append(doc)
        
        return retrieved_docs
    
    def get_collection_stats(self) -> Dict:
        """Get statistics about the collection"""
        count = self.collection.count()
        
        return {
            'collection_name': self.collection_name,
            'document_count': count,
            'persist_directory': settings.CHROMA_PERSIST_DIRECTORY
        }
    
    def delete_collection(self) -> None:
        """Delete the entire collection"""
        self.chroma_client.delete_collection(name=self.collection_name)
        print(f"Deleted collection: {self.collection_name}")
    
    def reset_collection(self) -> None:
        """Reset the collection (delete and recreate)"""
        try:
            self.delete_collection()
        except:
            pass
        
        self.collection = self.chroma_client.create_collection(
            name=self.collection_name,
            metadata={"description": "Government schemes knowledge base"}
        )
        print(f"Reset collection: {self.collection_name}")