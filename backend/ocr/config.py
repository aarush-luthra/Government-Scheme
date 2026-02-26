import pytesseract

# Path to Tesseract (Windows)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# English-only OCR
LANGUAGES = "eng"

# OCR configuration
TESSERACT_CONFIG = r"--oem 3 --psm 6"
