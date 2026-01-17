import re
from datetime import datetime

# -------------------------
# NORMALIZATION
# -------------------------
def normalize_text(text):
    text = text.upper()
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


# -------------------------
# GARBAGE WORD FILTER
# -------------------------
# Common OCR noise/garbage words to filter out from names
GARBAGE_WORDS = {
    'AAT', 'WET', 'WY', 'THE', 'OF', 'AND', 'IS', 'TO', 'IN', 'AT', 'ON',
    'FOR', 'BY', 'AN', 'AS', 'OR', 'IT', 'BE', 'IF', 'SO', 'NO', 'UP',
    'GOVERNMENT', 'INDIA', 'STATE', 'CERTIFICATE', 'CERTIFY', 'THAT',
    'THIS', 'DATE', 'BIRTH', 'PERMANENT', 'ADDRESS', 'INCOME', 'CASTE',
    'NAME', 'DOB', 'SON', 'DAUGHTER', 'WIFE', 'FATHER', 'MOTHER',
    'MALE', 'FEMALE', 'YEAR', 'OLD', 'AGE', 'RESIDENT', 'VILLAGE',
    'DISTRICT', 'TALUK', 'MANDAL', 'NUMBER', 'AADHAAR', 'PAN', 'UID',
    'VID', 'ISSUE', 'VALID', 'FROM', 'TILL', 'HEREBY', 'CERTIFIED'
}


def is_valid_name_word(word):
    """Check if a word looks like a valid name component."""
    # Must be alphabetic
    if not word.isalpha():
        return False
    # Must be at least 3 characters (filters noise like "WY", "AT")
    if len(word) < 3:
        return False
    # Must not be a garbage/common word
    if word in GARBAGE_WORDS:
        return False
    # Common Indian name patterns - should have vowels
    vowels = set('AEIOU')
    if not any(c in vowels for c in word):
        return False
    return True


# -------------------------
# DOCUMENT TYPE
# -------------------------
def detect_document_type(text):
    if "PERMANENT ACCOUNT NUMBER" in text or "INCOME TAX DEPARTMENT" in text:
        return "PAN"
    if re.search(r'\b\d{4}\s\d{4}\s\d{4}\b', text):
        return "AADHAAR"
    if "CASTE CERTIFICATE" in text or "SCHEDULED CASTE" in text or "SCHEDULED TRIBE" in text:
        return "CASTE_CERTIFICATE"
    if "INCOME CERTIFICATE" in text:
        return "INCOME_CERTIFICATE"
    return "UNKNOWN"


# -------------------------
# NAME
# -------------------------
def extract_name(text):
    # Pattern 1: Look for "NAME:" followed by the actual name
    match = re.search(r'NAME\s*[:\-]?\s*([A-Z][A-Z\s]{2,50}?)(?=\s*(?:S/O|D/O|W/O|DOB|DATE|MALE|FEMALE|FATHER|\d|$))', text)
    if match:
        name = clean_name(match.group(1))
        if name:
            return name

    # Pattern 2: Look for name after common prefixes
    match = re.search(r'(?:SHRI|SMT|KUM|MR|MRS|MS)\.?\s+([A-Z][A-Z\s]{2,50}?)(?=\s*(?:S/O|D/O|W/O|DOB|DATE|MALE|FEMALE|FATHER|AGE|\d|$))', text)
    if match:
        name = clean_name(match.group(1))
        if name:
            return name

    # Pattern 3: Extract consecutive valid name words
    tokens = text.split()
    name_tokens = []
    
    for token in tokens:
        if is_valid_name_word(token):
            name_tokens.append(token)
        else:
            # If we have at least 2 valid name words, stop
            if len(name_tokens) >= 2:
                break
            # Reset if we haven't found enough yet
            name_tokens = []

    if len(name_tokens) >= 2:
        return ' '.join(name_tokens)

    return None


def clean_name(name):
    """Clean extracted name by filtering out garbage words."""
    if not name:
        return None
    
    words = name.strip().split()
    valid_words = [w for w in words if is_valid_name_word(w)]
    
    if len(valid_words) >= 2:
        return ' '.join(valid_words)
    return None


# -------------------------
# DOB
# -------------------------
def extract_dob(text):
    # Pattern 1: With label (DATE OF BIRTH, DOB)
    match = re.search(
        r'(?:DATE\s*OF\s*BIRTH|DOB|D\.O\.B)\s*[:\-]?\s*(\d{1,2}[\-/\.]\d{1,2}[\-/\.]\d{2,4})',
        text
    )
    if match:
        return match.group(1)
    
    # Pattern 2: Standalone date DD/MM/YYYY or DD-MM-YYYY
    match = re.search(r'\b(\d{2}[\-/]\d{2}[\-/]\d{4})\b', text)
    if match:
        return match.group(1)
    
    return None


# -------------------------
# AGE CALCULATION
# -------------------------
def calculate_age(dob_string):
    """Calculate age from date of birth string."""
    if not dob_string:
        return None
    
    # Try different date formats
    date_formats = [
        '%d/%m/%Y', '%d-%m-%Y', '%d.%m.%Y',
        '%d/%m/%y', '%d-%m-%y', '%d.%m.%y'
    ]
    
    for fmt in date_formats:
        try:
            birth_date = datetime.strptime(dob_string, fmt)
            # Handle 2-digit years (assume 1900s for years > 50, 2000s otherwise)
            if birth_date.year > datetime.now().year:
                birth_date = birth_date.replace(year=birth_date.year - 100)
            
            today = datetime.now()
            age = today.year - birth_date.year
            
            # Adjust if birthday hasn't occurred yet this year
            if (today.month, today.day) < (birth_date.month, birth_date.day):
                age -= 1
            
            return age
        except ValueError:
            continue
    
    return None


# -------------------------
# CATEGORY
# -------------------------
def extract_category(text):
    if re.search(r'SCHEDULED\s+TRI', text):
        return "ST"
    if re.search(r'SCHEDULED\s+CAS', text):
        return "SC"
    if "OBC" in text:
        return "OBC"
    if "GENERAL" in text:
        return "GENERAL"
    return None


# -------------------------
# INCOME
# -------------------------
def extract_income(text):
    match = re.search(
        r'INCOME\s*(IS|OF)?\s*[:\-]?\s*RS\.?\s*(\d{3,})',
        text
    )
    if match:
        return int(match.group(2))

    match = re.search(r'INCOME\s*[:\-]?\s*(\d{3,})', text)
    if match:
        return int(match.group(1))

    return None


# -------------------------
# ID NUMBER
# -------------------------
def extract_id_number(text):
    pan = re.search(r'\b[A-Z]{5}[0-9]{4}[A-Z]\b', text)
    if pan:
        return pan.group(0)

    aadhaar = re.search(r'\b\d{4}\s\d{4}\s\d{4}\b', text)
    if aadhaar:
        return aadhaar.group(0)

    cert = re.search(
        r'(CERTIFICATE|REFERENCE|NO\.?|NUMBER)\s*[:\-]?\s*([A-Z0-9\/\-]+)',
        text
    )
    if cert:
        return cert.group(2)

    return None


# -------------------------
# MAIN
# -------------------------
def extract_all_fields(raw_text):
    text = normalize_text(raw_text)
    doc_type = detect_document_type(text)
    
    # Extract DOB
    dob = extract_dob(text)
    
    # Calculate age from DOB
    age = calculate_age(dob) if dob else None
    
    # Extract name from all document types (not just PAN/AADHAAR)
    name = extract_name(text)

    return {
        "document_type": doc_type,
        "name": name,
        "dob": dob,
        "age": age,
        "category": extract_category(text) if doc_type == "CASTE_CERTIFICATE" else None,
        "income": extract_income(text) if doc_type == "INCOME_CERTIFICATE" else None,
        "id_number": extract_id_number(text)
    }
