"""
MyScheme Loader - Loads government schemes from scraped JSON files.
Handles the dict-based format where scheme names are keys.
"""
import json
import os
import re
from typing import List, Dict, Any


# Category mapping from filename to readable name
CATEGORY_MAP = {
    "AgricultureEnvirronmentRural": "Agriculture, Rural & Environment",
    "BFSI": "Banking, Financial Services and Insurance",
    "BusinessEntrepreneurship": "Business & Entrepreneurship",
    "Education": "Education & Learning",
    "Health": "Health & Wellness",
    "Housing": "Housing & Shelter",
    "PublicSafety": "Public Safety, Law & Justice",
    "ScienceIT": "Science, IT & Communications",
    "Skills": "Skills & Employment",
    "SocialWelfare": "Social Welfare & Empowerment",
    "Sports": "Sports & Culture",
    "Transport": "Transport & Infrastructure",
    "Travel": "Travel & Tourism",
    "Utility": "Utility & Sanitation",
    "WomenChild": "Women and Child",
}


def extract_text_from_nested(data: Any) -> str:
    """
    Recursively extract text from nested JSON structures.
    Handles cases where benefits/eligibility/etc are lists of dicts with 'text' or 'children'.
    """
    if data is None:
        return ""
    
    if isinstance(data, str):
        return data.strip()
    
    if isinstance(data, list):
        parts = []
        for item in data:
            extracted = extract_text_from_nested(item)
            if extracted:
                parts.append(extracted)
        return "\n".join(parts)
    
    if isinstance(data, dict):
        # Check for direct text field
        if "text" in data:
            return data["text"].strip()
        
        # Check for children array
        if "children" in data:
            return extract_text_from_nested(data["children"])
        
        # Check for process in application_process
        if "process" in data:
            mode = data.get("mode", "general")
            process_text = extract_text_from_nested(data["process"])
            return f"[{mode.upper()}] {process_text}"
        
        # Fallback: try to join all values
        parts = []
        for value in data.values():
            if isinstance(value, (str, list, dict)):
                extracted = extract_text_from_nested(value)
                if extracted:
                    parts.append(extracted)
        return " ".join(parts)
    
    return str(data)


def format_application_process(app_process: Any) -> str:
    """Format application process from list of dicts to readable text."""
    if not app_process:
        return ""
    
    if isinstance(app_process, str):
        return app_process
    
    if isinstance(app_process, list):
        parts = []
        for item in app_process:
            if isinstance(item, dict):
                mode = item.get("mode", "general").upper()
                process = extract_text_from_nested(item.get("process", ""))
                if process:
                    parts.append(f"**{mode}:**\n{process}")
            else:
                parts.append(extract_text_from_nested(item))
        return "\n\n".join(parts)
    
    return extract_text_from_nested(app_process)


class MySchemeLoader:
    """
    Loads government schemes from scraped JSON files.
    The scraped files have scheme names as keys with details as values.
    """
    
    def __init__(self, data_dir: str = None):
        if data_dir is None:
            # Default to backend/data/schemes
            self.data_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "data",
                "schemes"
            )
        else:
            self.data_dir = data_dir
    
    def load_all_schemes(self, limit: int = None) -> List[Dict]:
        """Load all schemes from all JSON files in the data directory."""
        schemes: List[Dict] = []
        
        if not os.path.exists(self.data_dir):
            print(f"[WARN] Data directory not found: {self.data_dir}")
            return schemes
        
        for filename in os.listdir(self.data_dir):
            if not filename.endswith(".json"):
                continue
            
            file_path = os.path.join(self.data_dir, filename)
            
            # Skip empty or tiny files
            if os.path.getsize(file_path) < 10:
                print(f"[WARN] Skipping empty/invalid file: {filename}")
                continue
            
            # Extract category from filename
            category_key = filename.replace(".json", "")
            category = CATEGORY_MAP.get(category_key, category_key)
            
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                if not isinstance(data, dict):
                    print(f"[WARN] Skipping invalid format (not a dict): {filename}")
                    continue
                
                # Parse each scheme
                for scheme_name, scheme_data in data.items():
                    if not isinstance(scheme_data, dict):
                        continue
                    
                    scheme = self._parse_scheme(scheme_name, scheme_data, category)
                    if scheme:
                        schemes.append(scheme)
                
                print(f"[OK] Loaded {len(data)} schemes from {filename}")
                
            except json.JSONDecodeError as e:
                print(f"[ERROR] JSON error in {filename}: {e}")
                continue
            except Exception as e:
                print(f"[ERROR] Error loading {filename}: {e}")
                continue
        
        # Remove duplicates by title (case-insensitive)
        unique = {s["title"].lower(): s for s in schemes if s.get("title")}
        schemes = list(unique.values())
        
        print(f"\n[INFO] Total unique schemes loaded: {len(schemes)}")
        
        return schemes[:limit] if limit else schemes
    
    def _parse_scheme(self, name: str, data: Dict, category: str) -> Dict:
        """Parse a single scheme from the scraped format to the pipeline format."""
        try:
            # Extract and normalize fields
            details = extract_text_from_nested(data.get("details", ""))
            benefits = extract_text_from_nested(data.get("benefits", ""))
            eligibility = extract_text_from_nested(data.get("eligibility", ""))
            exclusions = extract_text_from_nested(data.get("exclusions", ""))
            documents = extract_text_from_nested(data.get("documents_required", ""))
            application = format_application_process(data.get("application_process", []))
            government = data.get("government", "Central")
            
            # Build description from details
            description = details if details else f"Government scheme: {name}"
            
            return {
                "title": name,
                "description": description,
                "benefits": benefits,
                "eligibility": eligibility,
                "exclusions": exclusions,
                "documents_required": documents,
                "application_process": application,
                "department": government,  # Map government to department
                "government": government,
                "category": category,
                "url": "",
                "source": "myscheme.gov.in",
            }
        except Exception as e:
            print(f"[WARN] Error parsing scheme '{name}': {e}")
            return None
