from langchain_chroma import Chroma
from backend.rag.embeddings import EmbeddingGenerator
from backend.config.settings import VECTOR_DB_DIR

class VectorStoreRetriever:
    def __init__(self):
        embedder = EmbeddingGenerator()

        # ✅ IMPORTANT: pass the embeddings object itself
        self.vectorstore = Chroma(
            persist_directory=VECTOR_DB_DIR,
            embedding_function=embedder.get_embedding_function(),
            collection_name="government_schemes"
        )

        if self.vectorstore is not None:
            print("VectorStoreRetriever initialized")
        else:
            print("VectorStoreRetriever initialization failed")

    def search(self, query: str, k: int = 4):
        return self.vectorstore.similarity_search(query, k=k)
