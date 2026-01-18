"""
OCR Pipeline for extracting text from government documents.
Uses EasyOCR for better accuracy with Indian documents.
"""

import io
import logging
from typing import Optional, List
from PIL import Image
import numpy as np

logger = logging.getLogger(__name__)

# Global EasyOCR reader (loaded once, reused)
_reader = None


def get_reader():
    """Get or initialize EasyOCR reader."""
    global _reader
    if _reader is None:
        import easyocr
        logger.info("Initializing EasyOCR reader (this may take a moment)...")
        # Support English and Hindi
        _reader = easyocr.Reader(['en', 'hi'], gpu=False)
        logger.info("EasyOCR reader initialized successfully")
    return _reader


def preprocess_image(image: Image.Image) -> Image.Image:
    """
    Preprocess image for better OCR accuracy.
    """
    # Convert to RGB if necessary (EasyOCR works with RGB)
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    # Resize if too small
    width, height = image.size
    if width < 1000:
        ratio = 1000 / width
        new_size = (int(width * ratio), int(height * ratio))
        image = image.resize(new_size, Image.Resampling.LANCZOS)
    
    return image


def extract_text_from_image(image_bytes: bytes) -> str:
    """
    Extract text from image bytes using EasyOCR.
    Supports English and Hindi.
    """
    try:
        image = Image.open(io.BytesIO(image_bytes))
        processed = preprocess_image(image)
        
        # Convert PIL Image to numpy array for EasyOCR
        img_array = np.array(processed)
        
        reader = get_reader()
        
        # Extract text
        results = reader.readtext(img_array, detail=0, paragraph=True)
        
        # Join all text blocks
        text = '\n'.join(results)
        
        logger.info(f"EasyOCR extracted {len(results)} text blocks")
        
        return text.strip()
    except Exception as e:
        logger.error(f"OCR processing failed: {str(e)}")
        raise ValueError(f"OCR processing failed: {str(e)}")


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """
    Extract text from PDF using pdf2image and EasyOCR.
    Processes first page only for verification purposes.
    """
    try:
        from pdf2image import convert_from_bytes
        
        # Convert first page to image
        images = convert_from_bytes(pdf_bytes, first_page=1, last_page=1)
        
        if not images:
            raise ValueError("Could not extract pages from PDF")
        
        # Process first page
        processed = preprocess_image(images[0])
        img_array = np.array(processed)
        
        reader = get_reader()
        results = reader.readtext(img_array, detail=0, paragraph=True)
        
        text = '\n'.join(results)
        
        return text.strip()
    except ImportError:
        raise ValueError("PDF processing requires pdf2image library")
    except Exception as e:
        logger.error(f"PDF OCR processing failed: {str(e)}")
        raise ValueError(f"PDF OCR processing failed: {str(e)}")


def process_document(file_bytes: bytes, content_type: str) -> str:
    """
    Process uploaded document and extract text.
    
    Args:
        file_bytes: Raw file bytes
        content_type: MIME type of the file
        
    Returns:
        Extracted text from document
    """
    if content_type in ['image/png', 'image/jpeg', 'image/jpg']:
        return extract_text_from_image(file_bytes)
    elif content_type == 'application/pdf':
        return extract_text_from_pdf(file_bytes)
    else:
        raise ValueError(f"Unsupported file type: {content_type}")
