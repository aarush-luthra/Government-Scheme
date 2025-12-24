from typing import Dict


def normalize_scheme(raw: Dict) -> Dict:
    return {
        "title": raw.get("title", ""),
        "description": raw.get("description", ""),
        "benefits": raw.get("benefits", ""),
        "eligibility": raw.get("eligibility", ""),
        "documents_required": raw.get("documents_required", ""),
        "application_process": raw.get("application_process", ""),
        "department": raw.get("department", ""),
        "category": raw.get("category", ""),
        "url": raw.get("url", ""),
        "source": raw.get("source", ""),
    }
