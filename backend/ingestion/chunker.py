from typing import List, Dict
from langchain.schema import Document
from config.settings import CHUNK_SIZE, CHUNK_OVERLAP


def chunk_scheme(scheme: Dict) -> List[Document]:
    text = f"""
Title: {scheme['title']}
Description: {scheme['description']}
Benefits: {scheme['benefits']}
Eligibility: {scheme['eligibility']}
Documents Required: {scheme['documents_required']}
Application Process: {scheme['application_process']}
"""

    chunks = []
    start = 0

    while start < len(text):
        end = start + CHUNK_SIZE
        chunk_text = text[start:end]

        chunks.append(
            Document(
                page_content=chunk_text,
                metadata={
                    "title": scheme["title"],
                    "category": scheme["category"],
                    "department": scheme["department"],
                    "source": scheme["source"],
                    "url": scheme["url"],
                },
            )
        )

        start = end - CHUNK_OVERLAP

    return chunks
