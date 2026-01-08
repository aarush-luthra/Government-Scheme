from dotenv import load_dotenv
load_dotenv()

from pydantic_settings import BaseSettings
from pathlib import Path
import os


BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")


class Settings(BaseSettings):
    # OpenAI
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

    # Embeddings
    EMBEDDING_MODEL: str = "text-embedding-3-small"

    # Chunking
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200

    # Vector DB
    CHROMA_COLLECTION_NAME: str = "government_schemes"
    CHROMA_PERSIST_DIRECTORY: str = str(
        BASE_DIR / "backend" / "data" / "chroma_db"
    )

    # LLM Extraction (NEW)
    LLM_EXTRACTION_MODEL: str = "gpt-4o-mini"
    LLM_EXTRACTION_TEMPERATURE: float = 0.0
    SEMANTIC_COLLECTION_NAME: str = "semantic_facts"
    EXTRACTION_CACHE_DIR: str = str(
        BASE_DIR / "backend" / "data" / "extracted"
    )

    class Config:
        env_file = ".env"
        case_sensitive = True


# ✅ singleton
settings = Settings()

# ✅ backward-compatible constants
CHUNK_SIZE = settings.CHUNK_SIZE
CHUNK_OVERLAP = settings.CHUNK_OVERLAP

# Backward compatibility for older imports
VECTOR_DB_DIR = settings.CHROMA_PERSIST_DIRECTORY
# Raw data directory (JSON / scraped data)
RAW_DATA_DIR = str(BASE_DIR / "backend" / "data")
