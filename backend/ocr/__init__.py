"""
OCR Module for Government Scheme Assistant
Handles document scanning and field extraction
"""

from .ocr_pipeline import run_ocr
from .extract_fields import extract_all_fields

__all__ = ['run_ocr', 'extract_all_fields']
