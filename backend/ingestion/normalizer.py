from typing import Dict


def normalize_scheme(raw: Dict) -> Dict:
    """
    Normalize scheme data to a consistent format for the chunker.
    Handles both old and new JSON structures.
    """
    return {
        "title": raw.get("title", ""),
        "description": raw.get("description", ""),
        "benefits": raw.get("benefits", "Not specified"),
        "eligibility": raw.get("eligibility", "Not specified"),
        "eligibility_criteria": raw.get("eligibility_criteria", {}),  # Structured criteria
        "exclusions": raw.get("exclusions", "None specified"),
        "documents_required": raw.get("documents_required", "Not specified"),
        "application_process": raw.get("application_process", "Not specified"),
        "department": raw.get("department", ""),
        "government": raw.get("government", ""),
        "level": raw.get("level", "Central"),  # Central or State level
        "category": raw.get("category", ""),
        "url": raw.get("url", ""),
        "source": raw.get("source", ""),
    }
