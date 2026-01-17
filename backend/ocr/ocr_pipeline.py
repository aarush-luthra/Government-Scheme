import os
import pytesseract

from backend.ocr.config import LANGUAGES, TESSERACT_CONFIG
from backend.ocr.preprocess import preprocess_image


def clean_text(text):
    # Keep English + numbers only
    cleaned = "".join(c for c in text if ord(c) < 128)
    lines = [line.strip() for line in cleaned.splitlines() if line.strip()]
    return "\n".join(lines)


def run_ocr(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    image = preprocess_image(file_path)

    text = pytesseract.image_to_string(
        image,
        lang=LANGUAGES,
        config=TESSERACT_CONFIG
    )

    return clean_text(text)
