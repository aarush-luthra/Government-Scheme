"""
PDF Ingestion Runner

Fast PDF ingestion pipeline using character-based chunking.
Loads PDFs → Chunks text → Embeds into ChromaDB.
"""

import hashlib
import logging
from typing import List
from pathlib import Path

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma

from backend.ingestion.pdf_loader import PDFLoader
from backend.rag.embeddings import EmbeddingGenerator
from backend.config.settings import settings, VECTOR_DB_DIR

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s  %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def generate_chunk_id(filename: str, page: int, content: str) -> str:
    """
    Generate a unique, deterministic ID for a chunk.
    This ensures re-running the pipeline doesn't create duplicates.
    """
    content_hash = hashlib.md5(content[:100].encode()).hexdigest()[:8]
    return f"pdf_{filename}_{page}_{content_hash}"


def chunk_documents(documents: List[Document]) -> List[Document]:
    """
    Split documents into smaller chunks suitable for RAG.
    
    Uses RecursiveCharacterTextSplitter for semantic chunking.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
        length_function=len,
    )
    
    chunked_docs = []
    
    for doc in documents:
        chunks = splitter.split_text(doc.page_content)
        
        for i, chunk_text in enumerate(chunks):
            chunk_doc = Document(
                page_content=chunk_text,
                metadata={
                    **doc.metadata,
                    "chunk_index": i,
                    "total_chunks": len(chunks)
                }
            )
            chunked_docs.append(chunk_doc)
    
    return chunked_docs


def run_pdf_ingestion(pdf_dir: str = None, force_reingest: bool = False):
    """
    Main ingestion pipeline for PDFs.
    
    Args:
        pdf_dir: Optional custom directory for PDFs
        force_reingest: If True, re-ingest all PDFs even if already indexed
    """
    print("=" * 50)
    print("PDF Ingestion Pipeline")
    print("=" * 50)
    
    # Step 1: Load PDFs
    print("\n📄 Step 1: Loading PDFs...")
    loader = PDFLoader(pdf_dir)
    raw_documents = loader.load_all_pdfs()
    
    if not raw_documents:
        print("No documents to process. Add PDFs to the pdfs directory.")
        return
    
    # Step 2: Chunk documents
    print("\n✂️  Step 2: Chunking documents...")
    chunked_documents = chunk_documents(raw_documents)
    print(f"Created {len(chunked_documents)} chunks from {len(raw_documents)} pages")
    
    # Step 3: Initialize ChromaDB and check for existing documents
    print("\n🔍 Step 3: Checking for existing documents...")
    embedder = EmbeddingGenerator()
    
    vectorstore = Chroma(
        persist_directory=VECTOR_DB_DIR,
        embedding_function=embedder.get_embedding_function(),
        collection_name="government_schemes"
    )
    
    # Generate IDs and filter out existing ones
    documents_to_add = []
    ids_to_add = []
    
    # Get existing IDs from the collection
    try:
        existing_data = vectorstore._collection.get()
        existing_ids = set(existing_data.get("ids", []))
        print(f"Found {len(existing_ids)} existing documents in collection")
    except Exception:
        existing_ids = set()
    
    for doc in chunked_documents:
        chunk_id = generate_chunk_id(
            doc.metadata["filename"],
            doc.metadata["page"],
            doc.page_content
        )
        
        if chunk_id not in existing_ids or force_reingest:
            documents_to_add.append(doc)
            ids_to_add.append(chunk_id)
    
    if not documents_to_add:
        print("✓ All documents already indexed. Nothing to add.")
        return
    
    print(f"Will add {len(documents_to_add)} new chunks ({len(chunked_documents) - len(documents_to_add)} already exist)")
    
    # Step 4: Add documents to ChromaDB
    print("\n📦 Step 4: Embedding and storing documents...")
    
    # Add documents with explicit IDs
    vectorstore.add_documents(
        documents=documents_to_add,
        ids=ids_to_add
    )
    
    print(f"\n✅ Successfully ingested {len(documents_to_add)} chunks!")
    print(f"   Collection now has {len(existing_ids) + len(documents_to_add)} total documents")
    
    # Print summary
    print("\n" + "=" * 50)
    print("Summary:")
    print(f"  PDFs processed: {len(loader.get_pdf_files())}")
    print(f"  Pages extracted: {len(raw_documents)}")
    print(f"  Chunks created: {len(chunked_documents)}")
    print(f"  New chunks added: {len(documents_to_add)}")
    print("=" * 50)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Ingest PDFs into ChromaDB")
    parser.add_argument("--dir", type=str, help="Custom PDF directory")
    parser.add_argument("--force", action="store_true", help="Force re-ingestion")
    
    args = parser.parse_args()
    
    run_pdf_ingestion(pdf_dir=args.dir, force_reingest=args.force)
