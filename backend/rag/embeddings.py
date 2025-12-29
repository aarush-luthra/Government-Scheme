from langchain_openai import OpenAIEmbeddings
import os

class EmbeddingGenerator:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is not set")

        self.embeddings = OpenAIEmbeddings(
            openai_api_key=api_key,
            model="text-embedding-3-small"
        )

    # ✅ Used by ingestion
    def embed_texts(self, texts: list[str]):
        return self.embeddings.embed_documents(texts)

    # ✅ Used by retriever / Chroma
    def embed_query(self, text: str):
        return self.embeddings.embed_query(text)

    # ✅ Convenience for Chroma
    def get_embedding_function(self):
        return self.embeddings
