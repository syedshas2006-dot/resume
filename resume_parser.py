"""
Resume Parser Module for AI Resume Analyzer
===========================================
Handles uploading, validation, and multi-format text extraction (PDF & DOCX).
Includes in-memory processing to preserve user privacy (no persistent storage).
Detects scanned / image-only PDFs and provides user-friendly error messages.
"""

import io
import os
from typing import Any, Dict, Optional, Tuple
from pypdf import PdfReader
from docx import Document


MAX_FILE_SIZE_MB = 5.0
MAX_FILE_SIZE_BYTES = int(MAX_FILE_SIZE_MB * 1024 * 1024)
ALLOWED_EXTENSIONS = {".pdf", ".docx"}


def validate_file(file_name: str, file_size: int) -> Tuple[bool, Optional[str]]:
    """
    Validates uploaded file extension and size.
    
    Args:
        file_name (str): Original filename
        file_size (int): Size in bytes
        
    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    if not file_name:
        return False, "No file uploaded. Please select a PDF or DOCX resume."

    ext = os.path.splitext(file_name)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return False, (
            f"Unsupported file format '{ext}'. "
            f"Please upload a text-based PDF (.pdf) or Word document (.docx)."
        )

    if file_size <= 0:
        return False, "The uploaded file is empty (0 bytes). Please upload a valid resume."

    if file_size > MAX_FILE_SIZE_BYTES:
        size_mb = file_size / (1024 * 1024)
        return False, (
            f"File size ({size_mb:.2f} MB) exceeds the {MAX_FILE_SIZE_MB:.0f} MB limit. "
            f"Please compress or upload a smaller file."
        )

    return True, None


def extract_text_from_pdf(file_bytes: bytes) -> Tuple[str, int, bool]:
    """
    Extracts text from all pages of a PDF file using pypdf.
    
    Args:
        file_bytes (bytes): Binary content of PDF
        
    Returns:
        Tuple[str, int, bool]: (extracted_text, page_count, is_scanned)
    """
    stream = io.BytesIO(file_bytes)
    reader = PdfReader(stream)
    page_count = len(reader.pages)
    
    extracted_pages = []
    for idx, page in enumerate(reader.pages):
        page_text = page.extract_text() or ""
        extracted_pages.append(page_text.strip())
        
    full_text = "\n\n".join(extracted_pages).strip()
    
    # Check if scanned/image-only PDF (less than 20 characters per page average or empty)
    is_scanned = False
    if page_count > 0 and len(full_text.split()) < 15:
        is_scanned = True
        
    return full_text, page_count, is_scanned


def extract_text_from_docx(file_bytes: bytes) -> Tuple[str, int]:
    """
    Extracts text from paragraphs and table cells of a DOCX file using python-docx.
    
    Args:
        file_bytes (bytes): Binary content of DOCX
        
    Returns:
        Tuple[str, int]: (extracted_text, element_count)
    """
    stream = io.BytesIO(file_bytes)
    doc = Document(stream)
    
    elements = []
    
    # 1. Paragraphs
    for p in doc.paragraphs:
        txt = p.text.strip()
        if txt:
            elements.append(txt)
            
    # 2. Tables (resumes often put skills or contact info in tables)
    for table in doc.tables:
        for row in table.rows:
            row_texts = [cell.text.strip() for cell in row.cells if cell.text.strip()]
            if row_texts:
                elements.append(" | ".join(row_texts))
                
    full_text = "\n".join(elements).strip()
    return full_text, len(elements)


def parse_resume(file_name: str, file_bytes: bytes) -> Dict[str, Any]:
    """
    Main entry point for resume ingestion and parsing.
    Validates file, extracts text, computes metadata, and protects user privacy.
    
    Args:
        file_name (str): Original uploaded file name
        file_bytes (bytes): Raw binary bytes of uploaded file
        
    Returns:
        Dict[str, Any]: Structured dictionary with extraction results & metadata
    """
    file_size = len(file_bytes)
    is_valid, validation_error = validate_file(file_name, file_size)
    
    if not is_valid:
        return {
            "status": "error",
            "file_name": file_name,
            "error_message": validation_error,
            "raw_text": "",
            "word_count": 0,
            "page_count": 0,
            "is_scanned": False,
        }
        
    ext = os.path.splitext(file_name)[1].lower()
    
    try:
        if ext == ".pdf":
            raw_text, page_count, is_scanned = extract_text_from_pdf(file_bytes)
            if is_scanned:
                return {
                    "status": "error",
                    "file_name": file_name,
                    "error_message": (
                        "Scanned or image-only PDF detected with no extractable text. "
                        "Our OCR is disabled in this basic version. "
                        "Please upload a text-selectable PDF or a Word document (.docx)."
                    ),
                    "raw_text": "",
                    "word_count": 0,
                    "page_count": page_count,
                    "is_scanned": True,
                }
        elif ext == ".docx":
            raw_text, element_count = extract_text_from_docx(file_bytes)
            page_count = max(1, element_count // 25)
            is_scanned = False
        else:
            return {
                "status": "error",
                "file_name": file_name,
                "error_message": f"Unsupported format: {ext}",
                "raw_text": "",
                "word_count": 0,
                "page_count": 0,
                "is_scanned": False,
            }
            
        # Check if text is essentially blank
        words = raw_text.split()
        if len(words) < 10:
            return {
                "status": "error",
                "file_name": file_name,
                "error_message": (
                    "The resume contains insufficient or empty text (less than 10 words). "
                    "Please upload a complete resume document."
                ),
                "raw_text": raw_text,
                "word_count": len(words),
                "page_count": page_count,
                "is_scanned": False,
            }
            
        return {
            "status": "success",
            "file_name": file_name,
            "file_type": ext.upper().replace(".", ""),
            "file_size_kb": round(file_size / 1024, 2),
            "raw_text": raw_text,
            "page_count": page_count,
            "word_count": len(words),
            "char_count": len(raw_text),
            "is_scanned": False,
            "error_message": None,
        }
        
    except Exception as exc:
        return {
            "status": "error",
            "file_name": file_name,
            "error_message": f"Failed to read file '{file_name}': {str(exc)}",
            "raw_text": "",
            "word_count": 0,
            "page_count": 0,
            "is_scanned": False,
        }
