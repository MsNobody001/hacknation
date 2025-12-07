import os
import logging

from django.conf import settings
from langchain_openai import AzureChatOpenAI

logger = logging.getLogger(__name__)


def get_azure_llm(
    temperature: float = 0.1,
    max_tokens: int = 4096
) -> AzureChatOpenAI:
    """
    Create and configure Azure OpenAI LLM instance.
    
    Args:
        temperature: Model temperature (0.0-1.0). Lower = more deterministic.
        max_tokens: Maximum tokens in response.
        
    Returns:
        Configured AzureChatOpenAI instance
    """
    return AzureChatOpenAI(
        azure_endpoint=os.environ.get(
            "AZURE_OPENAI_ENDPOINT",
            getattr(settings, "AZURE_OPENAI_ENDPOINT", "")
        ),
        azure_deployment=os.environ.get(
            "AZURE_OPENAI_DEPLOYMENT",
            getattr(settings, "AZURE_OPENAI_DEPLOYMENT", "gpt-4o")
        ),
        api_version=os.environ.get(
            "AZURE_OPENAI_API_VERSION",
            getattr(settings, "AZURE_OPENAI_API_VERSION", "2024-08-01-preview")
        ),
        api_key=os.environ.get(
            "AZURE_OPENAI_API_KEY",
            getattr(settings, "AZURE_OPENAI_API_KEY", None)
        ),
        temperature=temperature,
        max_tokens=max_tokens,
    )


def prepare_documents_context(ocr_results: list) -> list[dict]:
    """
    Prepare document data from OCR results for LLM processing.
    
    Args:
        ocr_results: List of OCRResult model instances
        
    Returns:
        List of document dictionaries with metadata and content
    """
    documents = []
    
    for ocr_result in ocr_results:
        document = ocr_result.document
        doc_type = document.document_type.name if document.document_type else "Nieznany typ"
        
        documents.append({
            "document_name": document.filename,
            "document_type": doc_type,
            "document_content": ocr_result.extracted_text,
            "confidence_score": ocr_result.confidence_score,
        })
    
    return documents


def prepare_combined_documents_text(ocr_results: list) -> str:
    """
    Prepare a single combined text from all OCR results for analysis.
    
    Args:
        ocr_results: List of OCRResult model instances
        
    Returns:
        Combined formatted string with all document contents
    """
    parts = []
    
    for i, ocr_result in enumerate(ocr_results, 1):
        document = ocr_result.document
        doc_type = document.document_type.name if document.document_type else "Nieznany typ"
        
        parts.append(f"""
=== DOKUMENT {i}: {document.filename} ===
Typ dokumentu: {doc_type}

{ocr_result.extracted_text}

--- Koniec dokumentu {i} ---
""")
    
    return "\n".join(parts)
