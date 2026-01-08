"""
ChromaDB Inspector

View and query the embedded data in ChromaDB to verify relevance.

Usage:
    python -m backend.ingestion.inspect_embeddings
    python -m backend.ingestion.inspect_embeddings --query "eligibility criteria"
    python -m backend.ingestion.inspect_embeddings --show 10
"""

from langchain_chroma import Chroma
from backend.rag.embeddings import EmbeddingGenerator
from backend.config.settings import VECTOR_DB_DIR, settings


def get_vectorstore():
    """Get the ChromaDB vectorstore."""
    embedder = EmbeddingGenerator()
    return Chroma(
        persist_directory=VECTOR_DB_DIR,
        embedding_function=embedder.get_embedding_function(),
        collection_name=settings.CHROMA_COLLECTION_NAME
    )


def show_all_chunks(limit: int = 10):
    """Display stored chunks."""
    vectorstore = get_vectorstore()
    data = vectorstore._collection.get(include=['documents', 'metadatas'])
    
    total = len(data["ids"])
    print(f"\n📊 Total chunks in database: {total}")
    print("=" * 60)
    
    for i in range(min(limit, total)):
        print(f"\n--- Chunk {i+1}/{total} ---")
        print(f"ID: {data['ids'][i]}")
        meta = data['metadatas'][i]
        print(f"Source: {meta.get('filename', 'unknown')} | Page: {meta.get('page', '?')}")
        content = data['documents'][i]
        # Show first 400 chars
        preview = content[:400] + "..." if len(content) > 400 else content
        print(f"Content:\n{preview}")
    
    if total > limit:
        print(f"\n... and {total - limit} more chunks. Use --show {total} to see all.")


def query_chunks(query: str, k: int = 5):
    """Query the vectorstore and show results."""
    vectorstore = get_vectorstore()
    
    print(f"\n🔍 Query: \"{query}\"")
    print("=" * 60)
    
    results = vectorstore.similarity_search_with_score(query, k=k)
    
    if not results:
        print("No results found.")
        return
    
    for i, (doc, score) in enumerate(results):
        print(f"\n--- Result {i+1} (score: {score:.4f}) ---")
        meta = doc.metadata
        print(f"Source: {meta.get('filename', 'unknown')} | Page: {meta.get('page', '?')}")
        content = doc.page_content
        preview = content[:500] + "..." if len(content) > 500 else content
        print(f"Content:\n{preview}")


def get_stats():
    """Get database statistics."""
    vectorstore = get_vectorstore()
    data = vectorstore._collection.get(include=['metadatas'])
    
    total = len(data["ids"])
    
    # Count by file
    files = {}
    for meta in data['metadatas']:
        fname = meta.get('filename', 'unknown')
        files[fname] = files.get(fname, 0) + 1
    
    print(f"\n📈 Database Statistics")
    print("=" * 40)
    print(f"Total chunks: {total}")
    print(f"Unique PDFs: {len(files)}")
    print(f"\nChunks per file:")
    for fname, count in sorted(files.items()):
        print(f"  {fname}: {count} chunks")


def export_to_file(limit: int = 50, output_path: str = None):
    """Export chunks to a readable text file."""
    vectorstore = get_vectorstore()
    data = vectorstore._collection.get(include=['documents', 'metadatas'])
    
    total = len(data["ids"])
    export_count = min(limit, total)
    
    if output_path is None:
        output_path = "backend/data/embedded_chunks.txt"
    
    with open(output_path, 'w') as f:
        f.write(f"ChromaDB Embedded Chunks Export\n")
        f.write(f"Total chunks in database: {total}\n")
        f.write(f"Exported: {export_count} chunks\n")
        f.write("=" * 60 + "\n\n")
        
        for i in range(export_count):
            f.write(f"--- Chunk {i+1} ---\n")
            f.write(f"ID: {data['ids'][i]}\n")
            meta = data['metadatas'][i]
            f.write(f"Source: {meta.get('filename', 'unknown')} | Page: {meta.get('page', '?')}\n")
            f.write(f"Content:\n{data['documents'][i]}\n")
            f.write("\n" + "-" * 40 + "\n\n")
    
    print(f"✅ Exported {export_count} chunks to: {output_path}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Inspect ChromaDB embeddings")
    parser.add_argument("--query", "-q", type=str, help="Query to search for")
    parser.add_argument("--show", "-s", type=int, default=5, help="Number of chunks to show")
    parser.add_argument("--stats", action="store_true", help="Show statistics only")
    parser.add_argument("--export", "-e", type=int, help="Export N chunks to file")
    parser.add_argument("--output", "-o", type=str, help="Output file path for export")
    
    args = parser.parse_args()
    
    if args.stats:
        get_stats()
    elif args.export:
        export_to_file(args.export, args.output)
    elif args.query:
        query_chunks(args.query, k=args.show)
    else:
        show_all_chunks(args.show)
