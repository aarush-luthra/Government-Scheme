from openai import OpenAI
from config.settings import OPENAI_API_KEY, EMBEDDING_MODEL


class EmbeddingGenerator:
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.model_name = EMBEDDING_MODEL

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        response = self.client.embeddings.create(
            model=self.model_name,
            input=texts,
        )
        return [item.embedding for item in response.data]
