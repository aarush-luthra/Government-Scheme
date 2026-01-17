"""
MyScheme API Scraper - Final Optimized Version
Features:
1. Multiprocessing (Configurable Concurrency)
2. Robust Rich Text Parsing (Extracts text from nested JSON blocks)
3. Rate Limiting (Exponential Backoff for 429/500 errors)
4. Overwrite Logic (Creates new file or overwrites existing)
"""

import requests
import json
import time
import os
import shutil
import urllib.parse
import multiprocessing
import random

# --- Configuration ---
API_KEY = "tYTy5eEhlu9rFjyxuCr7ra7ACp4dv1RH8gWuHTDc"
SEARCH_URL = "https://api.myscheme.gov.in/search/v6/schemes"
SCHEME_DETAIL_URL = "https://api.myscheme.gov.in/schemes/v6/public/schemes"

OUTPUT_DIR = "data"
PAGE_SIZE = 100

# Headers
headers = {
    "Content-Type": "application/json",
    "x-api-key": API_KEY,
    "Accept": "application/json",
    "Origin": "https://www.myscheme.gov.in",
    "Referer": "https://www.myscheme.gov.in/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# --- Helper: Request Handler with Exponential Backoff ---

def make_request_with_retry(url, max_retries=8):
    """
    Makes a GET request with exponential backoff.
    Waits longer if the server returns 429 (Too Many Requests).
    """
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers, timeout=30)

            if response.status_code == 200:
                return response.json()

            # 429 = Rate Limit, 5xx = Server Error
            if response.status_code == 429 or 500 <= response.status_code < 600:
                # Exponential backoff: 2s, 4s, 8s, 16s... + random jitter
                wait_time = (2 ** attempt) + random.uniform(1, 3)
                print(f"  [⚠️ Rate Limit {response.status_code}] Retrying in {wait_time:.1f}s...")
                time.sleep(wait_time)
                continue

            response.raise_for_status()

        except requests.exceptions.RequestException as e:
            wait_time = 2 + random.uniform(0, 1)
            print(f"  [⚠️ Error] {e}. Retrying in {wait_time:.1f}s...")
            time.sleep(wait_time)

    print(f"  [❌ FAIL] Max retries reached for: {url}")
    return None

# --- Helper: Rich Text Parsing (CRITICAL FOR YOUR DATA FORMAT) ---

def extract_text_from_blocks(blocks):
    """
    Recursively extracts text from the nested 'children' structure
    used in the MyScheme API rich text fields.
    """
    if not blocks:
        return ""

    # Handle simple strings (Markdown fallback)
    if isinstance(blocks, str):
        return blocks.strip()

    text_content = []

    if isinstance(blocks, list):
        for block in blocks:
            # Recursive handling for lists inside lists
            if isinstance(block, list):
                text_content.append(extract_text_from_blocks(block))
            elif isinstance(block, dict):
                # Direct text node
                if 'text' in block and block['text']:
                    text_content.append(block['text'])

                # Node with children (e.g., paragraph, list_item)
                if 'children' in block:
                    text_content.append(extract_text_from_blocks(block['children']))

                # Handle 'content' key (sometimes used instead of children)
                if 'content' in block:
                    text_content.append(extract_text_from_blocks(block['content']))

    return " ".join(filter(None, text_content)).strip()

def extract_application_process(process_data):
    """Parses the applicationProcess array into the specific format required."""
    results = []
    if not process_data or not isinstance(process_data, list):
        return results

    for item in process_data:
        mode = item.get('mode', 'Unknown')
        process_blocks = item.get('process', [])
        # Use the rich text extractor here
        process_text = extract_text_from_blocks(process_blocks)

        results.append({
            "mode": mode,
            "process": process_text
        })
    return results

def safe_get(data, *keys, default=""):
    """Safely navigate nested dictionary"""
    result = data
    for key in keys:
        if isinstance(result, dict):
            result = result.get(key)
        else:
            return default
        if result is None:
            return default
    return result if result is not None else default

# --- Core Processing Logic ---

def fetch_schemes_list(category, page_from=0, size=PAGE_SIZE):
    query = [{"identifier": "schemeCategory", "value": category}]
    query_json = json.dumps(query)
    query_encoded = urllib.parse.quote(query_json, safe='')
    url = f"{SEARCH_URL}?lang=en&q={query_encoded}&keyword=&sort=&from={page_from}&size={size}"
    return make_request_with_retry(url)

def fetch_scheme_detail(slug):
    url = f"{SCHEME_DETAIL_URL}?slug={slug}&lang=en"
    return make_request_with_retry(url)

def fetch_documents(scheme_id):
    url = f"{SCHEME_DETAIL_URL}/{scheme_id}/documents?lang=en"
    return make_request_with_retry(url)

def process_scheme(scheme_info):
    """
    Extracts data and formats it according to your specific requirements
    using the Rich Text Extractors.
    """
    fields = scheme_info.get('fields', scheme_info)
    slug = fields.get('slug', '')
    scheme_id = scheme_info.get('id', '')

    if not slug: return None, None

    # Fetch full details
    detail = fetch_scheme_detail(slug)
    if not detail or 'data' not in detail:
        return None, None

    # Navigate to the English data node
    en_data = detail.get('data', {}).get('en', {})

    # --- DATA SOURCE MAPPING ---
    basic_details = en_data.get('basicDetails', {})
    scheme_content = en_data.get('schemeContent', {})

    # FIXED: eligibilityCriteria is a SIBLING of schemeContent, not a child
    eligibility_criteria = en_data.get('eligibilityCriteria', {})

    # 1. Name
    scheme_name = basic_details.get('schemeName', '')

    # 2. Level (Central/State)
    level_data = basic_details.get('level', {})
    level = level_data.get('label', 'Unknown') if isinstance(level_data, dict) else str(level_data)

    # 3. Details
    # Strategy: Try Markdown (_md) first, then Block Parsing
    details_text = scheme_content.get('detailedDescription_md') or \
                   extract_text_from_blocks(scheme_content.get('detailedDescription', []))

    if not details_text:
        details_text = scheme_content.get('briefDescription', '')

    # 4. Benefits
    benefits_text = scheme_content.get('benefits_md') or \
                    extract_text_from_blocks(scheme_content.get('benefits', []))

    # 5. Eligibility (FIXED PATH & FALLBACK)
    # Checks eligibilityDescription_md OR eligibilityDescription inside eligibilityCriteria
    eligibility_text = eligibility_criteria.get('eligibilityDescription_md') or \
                       extract_text_from_blocks(eligibility_criteria.get('eligibilityDescription', []))

    # 6. Exclusions (FIXED PATH & FALLBACK)
    # Checks inside schemeContent
    exclusions_text = scheme_content.get('exclusions_md') or \
                      extract_text_from_blocks(scheme_content.get('exclusions', []))

    # 7. Application Process
    app_process_data = en_data.get('applicationProcess', [])
    application_process = extract_application_process(app_process_data)

    # 8. Documents Required
    # Strategy: Check schemeContent first, then fetch separate endpoint if needed
    docs_blocks = scheme_content.get('documentsRequired', [])
    documents_text = extract_text_from_blocks(docs_blocks)

    # Fallback: Fetch from separate documents API if missing
    if not documents_text and scheme_id:
        doc_res = fetch_documents(scheme_id)
        if doc_res:
            doc_data = safe_get(doc_res, 'data', 'en', default={})
            documents_text = doc_data.get('documentsRequired_md') or \
                             extract_text_from_blocks(doc_data.get('documentsRequired', []))

    # Construct Final Object
    scheme_data = {
        "details": details_text,
        "level": level,
        "benefits": benefits_text,
        "eligibility": eligibility_text,
        "exclusions": exclusions_text,
        "application process": application_process,
        "documents required": documents_text
    }

    return scheme_name, scheme_data

# --- Worker Process ---

def main_worker(args):
    category_name, output_file_name = args

    # Ensure directory exists (safe for multiple processes)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print(f"[START] Processing Category: {category_name}")

    # 1. Fetch Master List
    all_schemes = []
    page_from = 0
    total_count = None

    while True:
        result = fetch_schemes_list(category_name, page_from=page_from)
        if not result: break

        data = result.get('data', {})
        summary = data.get('summary', {})
        items = data.get('hits', {}).get('items', [])

        if total_count is None:
            total_count = summary.get('total', 0)

        if not items: break

        all_schemes.extend(items)
        page_from += PAGE_SIZE

        # Rate Limit Sleep between list pages
        time.sleep(random.uniform(1.0, 2.0))

        if page_from >= total_count: break

    print(f"[{category_name}] Found {len(all_schemes)} schemes. Fetching details...")

    # 2. Fetch Details
    schemes_data = {}

    for idx, scheme in enumerate(all_schemes, 1):
        try:
            scheme_name, scheme_data = process_scheme(scheme)
            if scheme_data:
                schemes_data[scheme_name] = scheme_data

            if idx % 10 == 0:
                print(f"[{category_name}] Progress: {idx}/{len(all_schemes)}")

            # Rate Limit Sleep between details (Large interval to avoid 429)
            time.sleep(random.uniform(1.5, 3.5))

        except Exception as e:
            print(f"[{category_name}] Error processing scheme: {e}")

    # 3. Save Final File (Overwrites existing file)
    output_path = os.path.join(OUTPUT_DIR, output_file_name)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(schemes_data, f, indent=2, ensure_ascii=False)

    print(f"[DONE] {category_name} -> Saved to {output_path}")

# --- Execution Entry Point ---

if __name__ == "__main__":
    # Create data directory
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # List of categories to scrape
    # Format: ("API Category Name", "Output Filename.json")
    categories_to_scrape = [
        ("Agriculture,Rural & Environment", "Agriculture.json"),
        ("Banking,Financial Services and Insurance", "Banking.json"),
        ("Business & Entrepreneurship", "Business.json"),
        ("Education & Learning", "Education.json"),
        ("Health & Wellness", "Health.json"),
        ("Housing & Shelter", "Housing.json"),
        ("Public Safety,Law & Justice", "Law.json"),
        ("Science,IT & Communications", "ScienceIT.json"),
        ("Skills & Employment", "Skills.json"),
        ("Social welfare & Empowerment", "SocialWelfare.json"),
        ("Sports & Culture", "Sports.json"),
        ("Transport & Infrastructure", "Transport.json"),
        ("Travel & Tourism", "Travel.json"),
        ("Utility & Sanitation", "Utility.json"),
        ("Women and Child", "WomenChild.json")
    ]

    print(f"Starting scraping for {len(categories_to_scrape)} categories.")

    # We limit to 4 processes to balance speed vs rate limits.
    # If you run 12 processes hitting the API continuously, you WILL get banned temporarily.
    # 4 processes * 2-second sleep = avg 2 requests/sec, which is safe.
    CONCURRENT_PROCESSES = 4

    print(f"Running {CONCURRENT_PROCESSES} concurrent processes...")

    with multiprocessing.Pool(processes=CONCURRENT_PROCESSES) as pool:
        pool.map(main_worker, categories_to_scrape)

    print("\n" + "=" * 60)
    print("ALL CATEGORIES SCRAPED SUCCESSFULLY")
    print("=" * 60)