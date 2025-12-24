import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

DATA_DIR = os.path.join(BASE_DIR, "data")
RAW_DATA_DIR = os.path.join(DATA_DIR, "raw")
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, "processed")
VECTOR_DB_DIR = os.path.join(DATA_DIR, "chroma_db")

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

EMBEDDING_MODEL = "text-embedding-3-small"

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
