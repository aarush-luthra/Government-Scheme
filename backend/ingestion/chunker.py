from typing import List, Dict
from langchain_core.documents import Document
from backend.config.settings import CHUNK_SIZE, CHUNK_OVERLAP


def chunk_scheme(scheme: Dict) -> List[Document]:
    """
    Convert a scheme into Document chunks for vector storage.
    Creates eligibility-focused chunks for better scheme matching.
    """
    documents = []
    
    # Get eligibility criteria if available
    eligibility_criteria = scheme.get("eligibility_criteria", {})
    
    # Base metadata for all chunks
    base_metadata = {
        "title": scheme["title"],
        "category": scheme["category"],
        "department": scheme.get("department", ""),
        "government": scheme.get("government", ""),
        "level": scheme.get("level", "Central"),
        "source": scheme.get("source", ""),
        "url": scheme.get("url", ""),
        # Structured eligibility for filtering
        "age_min": eligibility_criteria.get("age_min"),
        "age_max": eligibility_criteria.get("age_max"),
        "income_max": eligibility_criteria.get("income_max"),
        "gender": eligibility_criteria.get("gender"),
        "is_student": eligibility_criteria.get("is_student"),
        "is_disabled": eligibility_criteria.get("is_disabled"),
    }
    
    # Chunk 1: Eligibility-focused document (for matching user profiles)
    eligibility_text = f"""
SCHEME: {scheme['title']}
CATEGORY: {scheme['category']}
LEVEL: {scheme.get('level', 'Central')}

ELIGIBILITY CRITERIA:
{scheme['eligibility']}

EXCLUSIONS (WHO CANNOT APPLY):
{scheme.get('exclusions', 'None specified')}
"""
    
    eligibility_metadata = {**base_metadata, "chunk_type": "eligibility"}
    documents.append(Document(
        page_content=eligibility_text.strip(),
        metadata=eligibility_metadata
    ))
    
    # Chunk 2: Benefits and Description (for general queries)
    benefits_text = f"""
SCHEME: {scheme['title']}
CATEGORY: {scheme['category']}

DESCRIPTION:
{scheme['description']}

BENEFITS:
{scheme['benefits']}
"""
    
    benefits_metadata = {**base_metadata, "chunk_type": "benefits"}
    documents.append(Document(
        page_content=benefits_text.strip(),
        metadata=benefits_metadata
    ))
    
    # Chunk 3: Application Process (for how-to queries)
    application_text = f"""
SCHEME: {scheme['title']}

HOW TO APPLY:
{scheme['application_process']}

DOCUMENTS REQUIRED:
{scheme['documents_required']}
"""
    
    application_metadata = {**base_metadata, "chunk_type": "application"}
    documents.append(Document(
        page_content=application_text.strip(),
        metadata=application_metadata
    ))
    
    # If any chunk is too large, split it further
    final_documents = []
    for doc in documents:
        if len(doc.page_content) > CHUNK_SIZE * 2:
            # Split large chunks
            text = doc.page_content
            start = 0
            while start < len(text):
                end = start + CHUNK_SIZE
                chunk_text = text[start:end]
                final_documents.append(Document(
                    page_content=chunk_text,
                    metadata=doc.metadata
                ))
                start = end - CHUNK_OVERLAP
        else:
            final_documents.append(doc)
    
    return final_documents
