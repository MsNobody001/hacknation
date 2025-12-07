import os
import re
import logging
from typing import Tuple

from django.conf import settings
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient

logger = logging.getLogger(__name__)


def get_document_intelligence_client() -> DocumentIntelligenceClient:
    endpoint = os.environ.get(
        "AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT",
        getattr(settings, "AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT", "")
    )
    key = os.environ.get(
        "AZURE_DOCUMENT_INTELLIGENCE_KEY",
        getattr(settings, "AZURE_DOCUMENT_INTELLIGENCE_KEY", "")
    )
    
    if not endpoint or not key:
        raise ValueError(
            "Missing Azure Document Intelligence credentials. "
            "Set AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT and AZURE_DOCUMENT_INTELLIGENCE_KEY "
            "in environment variables or Django settings."
        )
    
    return DocumentIntelligenceClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(key),
    )


def analyze_pdf_from_bytes_sync(
    file_bytes: bytes,
    model_id: str = "prebuilt-read"
) -> dict:
    try:
        client = get_document_intelligence_client()
    except ValueError as e:
        return {
            'content': '',
            'confidence': 0.0,
            'page_count': 0,
            'success': False,
            'error': str(e)
        }
    
    try:
        poller = client.begin_analyze_document(
            model_id,
            file_bytes,
            content_type="application/pdf"
        )
        
        result = poller.result()
        
        # Extract content
        content = result.content if hasattr(result, 'content') else ""
        
        # Calculate average confidence from word-level data
        confidences = []
        if hasattr(result, 'pages'):
            for page in result.pages:
                if hasattr(page, 'words'):
                    for word in page.words:
                        if hasattr(word, 'confidence'):
                            confidences.append(word.confidence)
        
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        page_count = len(result.pages) if hasattr(result, 'pages') else 0
        
        return {
            'content': content,
            'confidence': round(avg_confidence, 4),
            'page_count': page_count,
            'success': True,
            'error': None
        }
        
    except Exception as e:
        logger.exception("Document Intelligence analysis failed")
        return {
            'content': '',
            'confidence': 0.0,
            'page_count': 0,
            'success': False,
            'error': str(e)
        }


def validate_pdf_bytes(file_bytes: bytes) -> Tuple[bool, str]:
    if not file_bytes:
        return False, "Plik jest pusty"
    
    if not file_bytes.startswith(b'%PDF-'):
        return False, "Plik nie jest poprawnym PDF (brak nagłówka %PDF-)"
    
    if len(file_bytes) < 1024:
        return False, "Plik PDF jest zbyt mały (< 1KB)"
    
    return True, ""


def extract_key_info_from_text(text: str) -> dict:
    info = {
        'has_date': False,
        'has_pesel': False,
        'has_nip': False,
        'dates': [],
        'pesels': [],
        'nips': []
    }
    
    # Date patterns (DD-MM-YYYY or YYYY-MM-DD)
    date_patterns = [
        r'\b\d{2}[-./]\d{2}[-./]\d{4}\b',
        r'\b\d{4}[-./]\d{2}[-./]\d{2}\b'
    ]
    for pattern in date_patterns:
        dates = re.findall(pattern, text)
        if dates:
            info['dates'].extend(dates)
            info['has_date'] = True
    
    # PESEL (11 digits)
    pesel_pattern = r'\b\d{11}\b'
    pesels = re.findall(pesel_pattern, text)
    if pesels:
        info['pesels'] = pesels
        info['has_pesel'] = True
    
    # NIP (10 digits with optional separators)
    nip_pattern = r'\b\d{3}[-\s]?\d{3}[-\s]?\d{2}[-\s]?\d{2}\b'
    nips = re.findall(nip_pattern, text)
    if nips:
        info['nips'] = nips
        info['has_nip'] = True
    
    return info
