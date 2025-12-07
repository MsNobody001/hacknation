import logging
from typing import Optional

from pydantic import BaseModel, Field

from .ocr_utils import (
    analyze_pdf_from_bytes_sync,
    validate_pdf_bytes,
    extract_key_info_from_text,
)

logger = logging.getLogger(__name__)


class DocumentOCRResult(BaseModel):
    """Result of OCR processing for a single document."""
    document_id: str = Field(description="UUID of the processed document")
    filename: str = Field(description="Original filename")
    success: bool = Field(description="Whether OCR succeeded")
    content_length: int = Field(default=0, description="Number of characters extracted")
    confidence_score: float = Field(default=0.0, description="Average OCR confidence")
    page_count: int = Field(default=0, description="Number of pages processed")
    error: Optional[str] = Field(default=None, description="Error message if failed")
    key_info: Optional[dict] = Field(default=None, description="Extracted key information")


class OCRProcessingResult(BaseModel):
    """Complete result of OCR processing for an analysis."""
    status: str = Field(description="Processing status: completed, partial, failed")
    documents_processed: int = Field(description="Number of documents processed")
    documents_succeeded: int = Field(description="Number of successful OCR extractions")
    documents_failed: int = Field(description="Number of failed OCR extractions")
    results: list[DocumentOCRResult] = Field(default_factory=list, description="Individual document results")
    message: str = Field(description="Summary message")


def _process_single_document(document) -> DocumentOCRResult:
    from clerk_assistant.models import OCRResult
    
    if hasattr(document, 'ocr_result') and document.ocr_result:
        logger.info(f"Document {document.filename} already has OCR result, skipping")
        return DocumentOCRResult(
            document_id=str(document.id),
            filename=document.filename,
            success=True,
            content_length=len(document.ocr_result.extracted_text),
            confidence_score=document.ocr_result.confidence_score or 0.0,
            page_count=0,
            error=None,
            key_info=extract_key_info_from_text(document.ocr_result.extracted_text),
        )
    
    try:
        document.file.open('rb')
        file_bytes = document.file.read()
        document.file.close()
    except Exception as e:
        logger.error(f"Failed to read file {document.filename}: {e}")
        return DocumentOCRResult(
            document_id=str(document.id),
            filename=document.filename,
            success=False,
            error=f"Failed to read file: {str(e)}",
        )
    
    is_valid, error_msg = validate_pdf_bytes(file_bytes)
    if not is_valid:
        logger.warning(f"Invalid PDF {document.filename}: {error_msg}")
        return DocumentOCRResult(
            document_id=str(document.id),
            filename=document.filename,
            success=False,
            error=f"Invalid PDF: {error_msg}",
        )
    
    logger.info(f"Running OCR on {document.filename}")
    ocr_result = analyze_pdf_from_bytes_sync(file_bytes)
    
    if not ocr_result['success']:
        logger.error(f"OCR failed for {document.filename}: {ocr_result['error']}")
        return DocumentOCRResult(
            document_id=str(document.id),
            filename=document.filename,
            success=False,
            error=ocr_result['error'],
        )
    

    OCRResult.objects.create(
        document=document,
        extracted_text=ocr_result['content'],
        confidence_score=ocr_result['confidence'],
    )
    
    key_info = extract_key_info_from_text(ocr_result['content'])
    
    logger.info(f"OCR completed for {document.filename}: "
               f"{len(ocr_result['content'])} chars, "
               f"{ocr_result['confidence']:.2%} confidence")
    
    return DocumentOCRResult(
        document_id=str(document.id),
        filename=document.filename,
        success=True,
        content_length=len(ocr_result['content']),
        confidence_score=ocr_result['confidence'],
        page_count=ocr_result['page_count'],
        error=None,
        key_info=key_info,
    )


def process_ocr(analysis_id: str) -> dict:
    from clerk_assistant.models import Analysis, Document
    
    try:
        analysis = Analysis.objects.get(id=analysis_id)
    except Analysis.DoesNotExist:
        logger.error(f"Analysis {analysis_id} not found")
        raise ValueError(f"Analysis {analysis_id} not found")
    
    documents = Document.objects.filter(analysis=analysis).select_related('document_type')
    
    if not documents.exists():
        logger.warning(f"No documents found for analysis {analysis_id}")
        return {
            "status": "skipped",
            "message": "No documents to process",
            "documents_processed": 0,
            "documents_succeeded": 0,
            "documents_failed": 0,
            "results": [],
        }
    
    logger.info(f"Starting OCR processing for analysis {analysis_id} "
               f"with {documents.count()} documents")
    
    results = []
    succeeded = 0
    failed = 0
    
    for document in documents:
        result = _process_single_document(document)
        results.append(result)
        
        if result.success:
            succeeded += 1
        else:
            failed += 1
    
    if failed == 0:
        status = "completed"
        message = f"All {succeeded} documents processed successfully"
    elif succeeded == 0:
        status = "failed"
        message = f"All {failed} documents failed OCR processing"
    else:
        status = "partial"
        message = f"{succeeded} documents succeeded, {failed} documents failed"
    
    logger.info(f"OCR processing completed for {analysis_id}: {message}")
    
    return {
        "status": status,
        "message": message,
        "documents_processed": len(results),
        "documents_succeeded": succeeded,
        "documents_failed": failed,
        "results": [r.model_dump() for r in results],
    }


# Synchronous wrapper for Celery tasks
def process_ocr_sync(analysis_id: str) -> dict:
    return process_ocr(analysis_id)
