"""
OCR API Routes for document scanning and verification.
Handles file upload, OCR processing, and field extraction.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any

from backend.ocr.ocr_pipeline import process_document
from backend.ocr.extract_fields import extract_fields_from_text


router = APIRouter(prefix="/api/v1", tags=["OCR"])


class OCRResponse(BaseModel):
    """Response model for OCR endpoint."""
    success: bool
    document_type: str
    extracted_fields: Dict[str, Any]
    message: Optional[str] = None


class OCRErrorResponse(BaseModel):
    """Error response model."""
    success: bool = False
    error: str
    message: str


# Maximum file size: 5MB
MAX_FILE_SIZE = 5 * 1024 * 1024

# Allowed MIME types
ALLOWED_TYPES = {
    'image/png': 'png',
    'image/jpeg': 'jpeg',
    'image/jpg': 'jpg',
    'application/pdf': 'pdf'
}


@router.post("/ocr", response_model=OCRResponse)
async def process_ocr_document(file: UploadFile = File(...)):
    """
    Process uploaded document using OCR and extract structured fields.
    
    Supports:
    - Image files: PNG, JPG/JPEG
    - PDF files (first page only)
    
    Maximum file size: 5MB
    
    Returns extracted fields including:
    - Document type (PAN, Aadhaar, Caste Certificate, Income Certificate)
    - Name, Age, Gender, Category, Income, ID numbers
    """
    # Validate content type
    content_type = file.content_type
    if content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {content_type}. Allowed types: PNG, JPG, PDF"
        )
    
    # Read file content
    try:
        content = await file.read()
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to read file: {str(e)}"
        )
    
    # Validate file size
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size is 5MB, got {len(content) / (1024*1024):.2f}MB"
        )
    
    # Process document with OCR
    try:
        raw_text = process_document(content, content_type)
    except ValueError as e:
        raise HTTPException(
            status_code=422,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"OCR processing failed: {str(e)}"
        )
    
    # Extract structured fields
    try:
        fields = extract_fields_from_text(raw_text)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Field extraction failed: {str(e)}"
        )
    
    return OCRResponse(
        success=True,
        document_type=fields.document_type,
        extracted_fields=fields.to_dict(),
        message="Document processed successfully"
    )
