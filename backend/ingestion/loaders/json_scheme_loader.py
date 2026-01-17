"""
JSON Scheme Loader - Loads government schemes from copied JSON files.
Strictly parses eligibility rules for accurate scheme recommendations.
"""
import json
import os
import re
import html
from typing import List, Dict, Any, Optional


# Category mapping from filename to readable name
CATEGORY_MAP = {
    "Agriculture": "Agriculture, Rural & Environment",
    "Banking": "Banking, Financial Services & Insurance",
    "Business": "Business & Entrepreneurship",
    "Education": "Education & Learning",
    "Health": "Health & Wellness",
    "Housing": "Housing & Shelter",
    "Law": "Public Safety, Law & Justice",
    "ScienceIT": "Science, IT & Communications",
    "Skills": "Skills & Employment",
    "SocialWelfare": "Social Welfare & Empowerment",
    "Sports": "Sports & Culture",
    "Transport": "Transport & Infrastructure",
    "Travel": "Travel & Tourism",
    "Utility": "Utility & Sanitation",
    "WomenChild": "Women and Child",
}


def clean_html_text(text: str) -> str:
    """Clean HTML entities and tags from text."""
    if not text:
        return ""
    
    # Decode HTML entities
    text = html.unescape(text)
    
    # Remove HTML tags
    text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'<[^>]+>', '', text)
    
    # Clean up whitespace
    text = re.sub(r'\n\s*\n', '\n\n', text)
    text = text.strip()
    
    return text


def extract_text_from_nested(data: Any) -> str:
    """
    Recursively extract text from nested JSON structures.
    Handles cases where fields are lists of dicts with 'text', 'process', etc.
    """
    if data is None:
        return ""
    
    if isinstance(data, str):
        return clean_html_text(data)
    
    if isinstance(data, list):
        parts = []
        for item in data:
            extracted = extract_text_from_nested(item)
            if extracted:
                parts.append(extracted)
        return "\n".join(parts)
    
    if isinstance(data, dict):
        # Check for process in application_process
        if "process" in data:
            mode = data.get("mode", "general")
            process_text = extract_text_from_nested(data["process"])
            return f"[{mode.upper()}] {process_text}"
        
        # Check for direct text field
        if "text" in data:
            return clean_html_text(data["text"])
        
        # Fallback: join all string values
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
        return "Not specified"
    
    if isinstance(app_process, str):
        return clean_html_text(app_process)
    
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
        return "\n\n".join(parts) if parts else "Not specified"
    
    return extract_text_from_nested(app_process)


def parse_eligibility_criteria(eligibility_text: str) -> Dict[str, Any]:
    """
    Extract structured eligibility criteria from eligibility text.
    Attempts to identify age, income, gender, state, category requirements.
    """
    criteria = {
        "age_min": None,
        "age_max": None,
        "income_max": None,
        "gender": None,  # 'male', 'female', 'any'
        "states": [],  # List of applicable states
        "categories": [],  # SC, ST, OBC, General, etc.
        "is_student": None,
        "is_disabled": None,
        "raw_text": eligibility_text
    }
    
    text_lower = eligibility_text.lower()
    
    # Age extraction
    age_patterns = [
        r'(\d+)\s*(?:to|-)\s*(\d+)\s*years?\s*(?:of\s*)?(?:age)?',
        r'(?:minimum|min)\s*(?:age)?\s*:?\s*(\d+)',
        r'(?:maximum|max)\s*(?:age)?\s*:?\s*(\d+)',
        r'(?:age|aged?)\s*(?:of|between|from)?\s*(\d+)',
        r'(?:below|under)\s*(\d+)\s*years?',
        r'(?:above|over)\s*(\d+)\s*years?',
    ]
    
    for pattern in age_patterns[:1]:
        match = re.search(pattern, text_lower)
        if match:
            groups = match.groups()
            if len(groups) >= 2 and groups[1]:
                criteria["age_min"] = int(groups[0])
                criteria["age_max"] = int(groups[1])
            break
    
    # Income extraction
    income_patterns = [
        r'(?:annual|yearly)\s*(?:family\s*)?income\s*(?:of\s*)?(?:not\s*exceed|upto|up\s*to|less\s*than|below)?\s*(?:Rs\.?|₹|INR)?\s*([\d,]+(?:\.\d+)?)\s*(?:lakh|lac|lakhs)?',
        r'(?:income|earning)\s*(?:limit|ceiling)?\s*(?:of\s*)?(?:Rs\.?|₹|INR)?\s*([\d,]+(?:\.\d+)?)\s*(?:lakh|lac|lakhs)?',
        r'(?:Rs\.?|₹|INR)\s*([\d,]+(?:\.\d+)?)\s*(?:lakh|lac|lakhs)?\s*(?:per\s*annum|p\.?a\.?|annual)',
    ]
    
    for pattern in income_patterns:
        match = re.search(pattern, text_lower)
        if match:
            income_str = match.group(1).replace(',', '')
            try:
                income = float(income_str)
                # Check if 'lakh' is mentioned
                if 'lakh' in text_lower[match.start():match.end()+10] or 'lac' in text_lower[match.start():match.end()+10]:
                    income = income * 100000
                criteria["income_max"] = int(income)
            except:
                pass
            break
    
    # Gender detection
    if 'women' in text_lower or 'female' in text_lower or 'girl' in text_lower or 'widow' in text_lower:
        if 'men' not in text_lower and 'male' not in text_lower.replace('female', ''):
            criteria["gender"] = "female"
    elif 'men' in text_lower or 'male' in text_lower:
        if 'women' not in text_lower and 'female' not in text_lower:
            criteria["gender"] = "male"
    
    # Category detection (SC/ST/OBC)
    if re.search(r'\bsc\b|scheduled\s*caste', text_lower):
        criteria["categories"].append("SC")
    if re.search(r'\bst\b|scheduled\s*tribe', text_lower):
        criteria["categories"].append("ST")
    if re.search(r'\bobc\b|other\s*backward\s*class', text_lower):
        criteria["categories"].append("OBC")
    if re.search(r'\bgeneral\b', text_lower):
        criteria["categories"].append("General")
    
    # Disability detection
    if re.search(r'disab|handicap|divyang|pwd|person\s*with\s*disab', text_lower):
        criteria["is_disabled"] = True
    
    # Student detection
    if re.search(r'student|studying|enrolled|pursuing|class\s*\d', text_lower):
        criteria["is_student"] = True
    
    return criteria


class JSONSchemeLoader:
    """
    Loads government schemes from JSON files in backend/data/schemes_json/.
    Strictly parses eligibility rules for accurate recommendations.
    """
    
    def __init__(self, data_dir: str = None):
        if data_dir is None:
            # Default to backend/data/schemes_json
            self.data_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "data",
                "schemes_json"
            )
        else:
            self.data_dir = data_dir
    
    def load_all_schemes(self, limit: int = None) -> List[Dict]:
        """Load all schemes from all JSON files in the data directory."""
        schemes: List[Dict] = []
        
        if not os.path.exists(self.data_dir):
            print(f"[ERROR] Data directory not found: {self.data_dir}")
            return schemes
        
        for filename in sorted(os.listdir(self.data_dir)):
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
                file_scheme_count = 0
                for scheme_name, scheme_data in data.items():
                    if not isinstance(scheme_data, dict):
                        continue
                    
                    scheme = self._parse_scheme(scheme_name, scheme_data, category)
                    if scheme:
                        schemes.append(scheme)
                        file_scheme_count += 1
                
                print(f"[OK] Loaded {file_scheme_count} schemes from {filename}")
                
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
    
    def _parse_scheme(self, name: str, data: Dict, category: str) -> Optional[Dict]:
        """Parse a single scheme from JSON format to pipeline format."""
        try:
            # Extract and clean fields
            details = extract_text_from_nested(data.get("details", ""))
            benefits = extract_text_from_nested(data.get("benefits", ""))
            eligibility_raw = extract_text_from_nested(data.get("eligibility", ""))
            exclusions = extract_text_from_nested(data.get("exclusions", ""))
            documents = extract_text_from_nested(data.get("documents required", ""))
            application = format_application_process(data.get("application process", []))
            level = data.get("level", "Central")  # Central or State
            
            # Parse eligibility into structured criteria
            eligibility_criteria = parse_eligibility_criteria(eligibility_raw)
            
            # Build description from details
            description = details if details else f"Government scheme: {name}"
            
            return {
                "title": name,
                "description": description,
                "benefits": benefits if benefits else "Not specified",
                "eligibility": eligibility_raw if eligibility_raw else "Not specified",
                "eligibility_criteria": eligibility_criteria,  # Structured criteria
                "exclusions": exclusions if exclusions else "None specified",
                "documents_required": documents if documents else "Not specified",
                "application_process": application,
                "level": level,  # Central or State
                "government": level,  # Backward compatibility
                "department": level,
                "category": category,
                "url": "",
                "source": "myscheme.gov.in",
            }
        except Exception as e:
            print(f"[WARN] Error parsing scheme '{name}': {e}")
            return None
