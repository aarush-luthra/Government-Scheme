"""
Scheme Links Loader
Loads and provides lookup for official_site and apply_link from scheme_links.json
"""
import json
import os
from typing import Dict, Optional, Tuple
from functools import lru_cache

# Path to the scheme links JSON file
SCHEME_LINKS_PATH = os.path.join(
    os.path.dirname(__file__), 
    "..", "data", "raw", "scheme_links.json"
)

@lru_cache(maxsize=1)
def load_scheme_links() -> Dict[str, Dict[str, str]]:
    """
    Load scheme links from JSON file and create a lookup dictionary.
    Returns a dict: { normalized_scheme_name: { "official_site": ..., "apply_link": ... } }
    """
    try:
        with open(SCHEME_LINKS_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Create lookup with normalized (lowercase) scheme names
        lookup = {}
        for entry in data:
            name = entry.get("scheme_name", "").strip().lower()
            if name:
                lookup[name] = {
                    "official_site": entry.get("official_site", "NOT_AVAILABLE"),
                    "apply_link": entry.get("apply_link", "NOT_AVAILABLE")
                }
        
        print(f"[INFO] Loaded {len(lookup)} scheme links from scheme_links.json")
        return lookup
    except Exception as e:
        print(f"[ERROR] Failed to load scheme links: {e}")
        return {}


def normalize_name(name: str) -> str:
    """Normalize scheme name for matching."""
    import re
    name = name.strip().lower()
    # Remove common suffixes/prefixes that cause mismatches
    name = re.sub(r'\s*-\s*(central|state|scheme|yojana|yojna|programme|program)$', '', name, flags=re.IGNORECASE)
    # Remove special characters and extra spaces
    name = re.sub(r'[^\w\s]', ' ', name)
    name = re.sub(r'\s+', ' ', name).strip()
    return name


def get_scheme_links(scheme_name: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Get official_site and apply_link for a given scheme name.
    Uses fuzzy matching for better results.
    
    Args:
        scheme_name: The name of the scheme (case-insensitive)
    
    Returns:
        Tuple of (official_site, apply_link). Each is None if "NOT_AVAILABLE" or not found.
    """
    lookup = load_scheme_links()
    normalized_name = normalize_name(scheme_name)
    
    # Try exact match first (on normalized name)
    entry = lookup.get(normalized_name)
    
    if not entry:
        # Try to find in original lookup keys (already lowercase)
        for key in lookup:
            normalized_key = normalize_name(key)
            # Check if one contains the other (substring match)
            if normalized_name in normalized_key or normalized_key in normalized_name:
                entry = lookup[key]
                break
            # Check for word overlap (at least 60% words match)
            name_words = set(normalized_name.split())
            key_words = set(normalized_key.split())
            if name_words and key_words:
                overlap = len(name_words & key_words) / min(len(name_words), len(key_words))
                if overlap >= 0.6:
                    entry = lookup[key]
                    break
    
    if entry:
        official = entry.get("official_site")
        apply_link = entry.get("apply_link")
        
        # Convert "NOT_AVAILABLE" to None
        official = None if official == "NOT_AVAILABLE" else official
        apply_link = None if apply_link == "NOT_AVAILABLE" else apply_link
        
        return (official, apply_link)
    
    return (None, None)


def format_scheme_links(scheme_name: str) -> str:
    """
    Format scheme links as a string for inclusion in chatbot responses.
    Only includes links that are available.
    
    Args:
        scheme_name: The name of the scheme
    
    Returns:
        Formatted string with links, or empty string if no links available.
    """
    official, apply_link = get_scheme_links(scheme_name)
    
    links = []
    if official:
        links.append(f"Official Website: {official}")
    if apply_link:
        links.append(f"Apply Here: {apply_link}")
    
    if links:
        return "\n".join(links)
    return ""
