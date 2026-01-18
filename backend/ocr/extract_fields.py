"""
Field extraction from OCR text for government documents.
Extracts structured data from PAN, Aadhaar, Caste Certificate, Income Certificate.
"""

import re
import logging
from datetime import datetime
from typing import Dict, Optional, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


# -------------------------
# GARBAGE WORD FILTER
# -------------------------
GARBAGE_WORDS = {
    'AAT', 'WET', 'WY', 'THE', 'OF', 'AND', 'IS', 'TO', 'IN', 'AT', 'ON',
    'FOR', 'BY', 'AN', 'AS', 'OR', 'IT', 'BE', 'IF', 'SO', 'NO', 'UP',
    'GOVERNMENT', 'INDIA', 'STATE', 'CERTIFICATE', 'CERTIFY', 'THAT',
    'THIS', 'DATE', 'BIRTH', 'PERMANENT', 'ADDRESS', 'INCOME', 'CASTE',
    'NAME', 'DOB', 'SON', 'DAUGHTER', 'WIFE', 'FATHER', 'MOTHER',
    'MALE', 'FEMALE', 'YEAR', 'OLD', 'AGE', 'RESIDENT', 'VILLAGE',
    'DISTRICT', 'TALUK', 'MANDAL', 'NUMBER', 'AADHAAR', 'PAN', 'UID',
    'VID', 'ISSUE', 'VALID', 'FROM', 'TILL', 'HEREBY', 'CERTIFIED',
    'TAX', 'DEPARTMENT', 'ACCOUNT', 'REPUBLIC', 'SIGNED', 'ISSUING',
    'AUTHORITY', 'SIGNATURE', 'GOVT', 'CARD', 'UNIQUE', 'IDENTIFICATION',
    'SOT', 'UNK', 'HEALEY', 'FERFSA', 'QRS', 'XYZ', 'ABC', 'DEF', 'GHI'
}


@dataclass
class ExtractedFields:
    """Structured fields extracted from document."""
    document_type: str
    name: Optional[str] = None
    date_of_birth: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    category: Optional[str] = None
    annual_income: Optional[int] = None
    pan_number: Optional[str] = None
    aadhaar_number: Optional[str] = None
    raw_text: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "document_type": self.document_type,
            "name": self.name,
            "date_of_birth": self.date_of_birth,
            "age": self.age,
            "gender": self.gender,
            "category": self.category,
            "annual_income": self.annual_income,
            "pan_number": self.pan_number,
            "aadhaar_number": self.aadhaar_number,
            "raw_text": self.raw_text[:500] if self.raw_text else ""
        }


def normalize_text(text: str) -> str:
    """Normalize text for easier pattern matching."""
    text = text.upper()
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def is_valid_name_word(word: str) -> bool:
    """Check if a word looks like a valid name component."""
    if not word.isalpha():
        return False
    if len(word) < 3:
        return False
    if word in GARBAGE_WORDS:
        return False
    vowels = set('AEIOU')
    if not any(c in vowels for c in word):
        return False
    return True


def clean_name(name: str) -> Optional[str]:
    """Clean extracted name by filtering out garbage words."""
    if not name:
        return None
    words = name.strip().split()
    valid_words = [w for w in words if is_valid_name_word(w)]
    if len(valid_words) >= 2:
        return ' '.join(valid_words[:4]).title()
    elif len(valid_words) == 1 and len(valid_words[0]) > 4:
        return valid_words[0].title()
    return None


def detect_document_type(text: str) -> str:
    """Detect the type of government document from OCR text."""
    normalized = normalize_text(text)
    
    if "PERMANENT ACCOUNT NUMBER" in normalized or "INCOME TAX DEPARTMENT" in normalized:
        return "PAN Card"
    if re.search(r'\b\d{4}\s*\d{4}\s*\d{4}\b', normalized) or 'AADHAAR' in normalized:
        return "Aadhaar Card"
    if "CASTE CERTIFICATE" in normalized or "SCHEDULED CASTE" in normalized or "SCHEDULED TRIBE" in normalized:
        return "Caste Certificate"
    if "INCOME CERTIFICATE" in normalized:
        return "Income Certificate"
    return "Unknown Document"


def extract_name(text: str) -> Optional[str]:
    """Extract name from document text using multiple strategies."""
    normalized = normalize_text(text)
    lines = text.upper().split('\n') if '\n' in text else [normalized]
    
    # Strategy 1: Look for line after "NAME" label
    for i, line in enumerate(lines):
        if re.search(r'\bNAME\b', line):
            # Check the same line after NAME
            after_name = re.sub(r'.*\bNAME\b\s*[:/]?\s*', '', line)
            name = clean_name(after_name)
            if name:
                logger.info(f"Extracted name (after NAME label): {name}")
                return name
            # Check the next line
            if i + 1 < len(lines):
                name = clean_name(lines[i + 1])
                if name:
                    logger.info(f"Extracted name (next line after NAME): {name}")
                    return name
    
    # Strategy 2: Look for "NAME:" followed by the actual name
    match = re.search(r'NAME\s*[:\-/]?\s*([A-Z][A-Z\s]{2,50}?)(?=\s*(?:S/O|D/O|W/O|DOB|DATE|MALE|FEMALE|FATHER|\d|$))', normalized)
    if match:
        name = clean_name(match.group(1))
        if name:
            logger.info(f"Extracted name (pattern 2): {name}")
            return name

    # Strategy 3: Look for name after common prefixes
    match = re.search(r'(?:SHRI|SMT|KUM|MR|MRS|MS)\.?\s+([A-Z][A-Z\s]{2,50}?)(?=\s*(?:S/O|D/O|W/O|DOB|DATE|MALE|FEMALE|FATHER|AGE|\d|$))', normalized)
    if match:
        name = clean_name(match.group(1))
        if name:
            logger.info(f"Extracted name (pattern 3): {name}")
            return name

    # Strategy 4: Extract consecutive valid name words (fallback)
    tokens = normalized.split()
    name_tokens = []
    
    for token in tokens:
        if is_valid_name_word(token):
            name_tokens.append(token)
        else:
            if len(name_tokens) >= 2:
                break
            name_tokens = []

    if len(name_tokens) >= 2:
        name = ' '.join(name_tokens).title()
        logger.info(f"Extracted name (fallback): {name}")
        return name

    return None


def extract_dob(text: str) -> Optional[str]:
    """Extract date of birth from document text."""
    # Clean OCR noise: O -> 0, l -> 1, etc.
    cleaned = text.replace('O', '0').replace('o', '0')
    cleaned = re.sub(r'[~\|\\]', '', cleaned)  # Remove common OCR noise
    normalized = normalize_text(cleaned)
    
    # Pattern 1: With label (DATE OF BIRTH, DOB, जन्म तिथि)
    match = re.search(
        r'(?:DATE\s*OF\s*BIRTH|DOB|D\.O\.B|जन्म\s*तिथि|जन्म\s*तारीख)\s*[:\-/]?\s*(\d{1,2}[\-/\.]\d{1,2}[\-/\.]\d{2,4})',
        normalized
    )
    if match:
        dob = match.group(1)
        logger.info(f"Extracted DOB (with label): {dob}")
        return dob
    
    # Pattern 2: Standalone date DD/MM/YYYY or DD-MM-YYYY (more flexible)
    match = re.search(r'(\d{1,2}[\-/\.]\d{1,2}[\-/\.]\d{4})', normalized)
    if match:
        dob = match.group(1)
        logger.info(f"Extracted DOB (standalone): {dob}")
        return dob
    
    # Pattern 3: Try original text with flexible pattern (handles OCR noise)
    match = re.search(r'(\d{1,2})\s*[/\-\.]\s*(\d{1,2})\s*[/\-\.]\s*(\d{4})', text)
    if match:
        dob = f"{match.group(1)}/{match.group(2)}/{match.group(3)}"
        logger.info(f"Extracted DOB (flexible): {dob}")
        return dob
    
    return None


def calculate_age(dob_string: str) -> Optional[int]:
    """Calculate age from date of birth string."""
    if not dob_string:
        return None
    
    date_formats = [
        '%d/%m/%Y', '%d-%m-%Y', '%d.%m.%Y',
        '%d/%m/%y', '%d-%m-%y', '%d.%m.%y'
    ]
    
    for fmt in date_formats:
        try:
            birth_date = datetime.strptime(dob_string, fmt)
            if birth_date.year > datetime.now().year:
                birth_date = birth_date.replace(year=birth_date.year - 100)
            
            today = datetime.now()
            age = today.year - birth_date.year
            
            if (today.month, today.day) < (birth_date.month, birth_date.day):
                age -= 1
            
            return age
        except ValueError:
            continue
    
    return None


def extract_gender(text: str) -> Optional[str]:
    """Extract gender from document text."""
    normalized = normalize_text(text)
    
    if re.search(r'[/\s]MALE\b', normalized) or 'पुरुष' in text:
        return 'male'
    elif re.search(r'[/\s]FEMALE\b', normalized) or 'महिला' in text or 'स्त्री' in text:
        return 'female'
    elif re.search(r'\bMALE\b', normalized):
        return 'male'
    elif re.search(r'\bFEMALE\b', normalized):
        return 'female'
    
    return None


def extract_category(text: str) -> Optional[str]:
    """Extract social category from document text."""
    normalized = normalize_text(text)
    
    if re.search(r'SCHEDULED\s+TRI', normalized):
        return 'st'
    if re.search(r'SCHEDULED\s+CAS', normalized):
        return 'sc'
    if 'OBC' in normalized:
        return 'obc'
    if 'GENERAL' in normalized:
        return 'general'
    
    return None


def extract_income(text: str) -> Optional[int]:
    """Extract annual income from document text."""
    normalized = normalize_text(text)
    
    match = re.search(r'INCOME\s*(IS|OF)?\s*[:\-]?\s*RS\.?\s*(\d{3,})', normalized)
    if match:
        return int(match.group(2))

    match = re.search(r'INCOME\s*[:\-]?\s*(\d{3,})', normalized)
    if match:
        return int(match.group(1))

    return None


def extract_pan(text: str) -> Optional[str]:
    """Extract PAN number from document text."""
    match = re.search(r'\b([A-Z]{5}[0-9]{4}[A-Z])\b', text.upper())
    return match.group(1) if match else None


def extract_aadhaar(text: str) -> Optional[str]:
    """Extract Aadhaar number from document text."""
    match = re.search(r'\b(\d{4}\s+\d{4}\s+\d{4})\b', text)
    if match:
        return match.group(1)
    
    text_clean = re.sub(r'\s+', '', text)
    match = re.search(r'(\d{12})', text_clean)
    if match:
        aadhaar = match.group(1)
        return f"{aadhaar[:4]} {aadhaar[4:8]} {aadhaar[8:12]}"
    return None


def extract_fields_from_text(text: str) -> ExtractedFields:
    """
    Extract all relevant fields from OCR text.
    """
    logger.info(f"OCR Raw Text (first 500 chars): {text[:500]}")
    
    doc_type = detect_document_type(text)
    logger.info(f"Detected document type: {doc_type}")
    
    fields = ExtractedFields(
        document_type=doc_type,
        raw_text=text
    )
    
    # Extract name
    fields.name = extract_name(text)
    
    # Extract DOB and calculate age
    dob = extract_dob(text)
    if dob:
        fields.date_of_birth = dob
        fields.age = calculate_age(dob)
        logger.info(f"Extracted DOB: {dob}, calculated age: {fields.age}")
    
    # Extract gender
    fields.gender = extract_gender(text)
    
    # Document-specific extraction
    if doc_type == 'PAN Card':
        fields.pan_number = extract_pan(text)
    elif doc_type == 'Aadhaar Card':
        fields.aadhaar_number = extract_aadhaar(text)
    elif doc_type == 'Caste Certificate':
        fields.category = extract_category(text)
    elif doc_type == 'Income Certificate':
        fields.annual_income = extract_income(text)
        fields.category = extract_category(text)
    
    logger.info(f"Final extraction: name={fields.name}, age={fields.age}, gender={fields.gender}")
    
    return fields
