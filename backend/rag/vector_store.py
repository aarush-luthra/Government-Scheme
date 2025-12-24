import chromadb
from config.settings import VECTOR_DB_DIR


class VectorStore:
    def __init__(self, collection_name="government_schemes"):
        self.client = chromadb.PersistentClient(path=VECTOR_DB_DIR)
        self.collection = self.client.get_or_create_collection(collection_name)

    def add_documents(self, documents, embeddings):
        ids = [f"{doc.metadata['title']}_{i}" for i, doc in enumerate(documents)]

        self.collection.add(
            documents=[doc.page_content for doc in documents],
            metadatas=[doc.metadata for doc in documents],
            embeddings=embeddings,
            ids=ids,
        )
