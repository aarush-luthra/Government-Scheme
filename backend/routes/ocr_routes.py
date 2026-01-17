from fastapi import APIRouter, UploadFile, File
import os, uuid, shutil

from backend.ocr.ocr_pipeline import run_ocr
from backend.ocr.extract_fields import extract_all_fields

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/ocr")
async def run_ocr_on_document(file: UploadFile = File(...)):
    file_path = os.path.join(
        UPLOAD_DIR,
        f"{uuid.uuid4()}_{file.filename}"
    )

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    ocr_text = run_ocr(file_path)
    fields = extract_all_fields(ocr_text)

    os.remove(file_path)

    return {
        "ocr_text": ocr_text,
        "extracted_fields": fields
    }
