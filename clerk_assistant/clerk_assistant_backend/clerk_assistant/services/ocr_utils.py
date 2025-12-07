"""
OCR utility functions for Azure Document Intelligence integration
"""

import asyncio
from typing import Optional, Tuple
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence.aio import DocumentIntelligenceClient as AsyncDocumentIntelligenceClient
from azure.ai.documentintelligence import DocumentIntelligenceClient
import os


async def analyze_pdf_from_bytes(
    file_bytes: bytes,
    endpoint: str = None,
    key: str = None,
    model_id: str = "prebuilt-read"
) -> dict:
    """
    Analizuje dokument PDF z bytes i zwraca wyekstraktowana zawartosc.
    Wersja asynchroniczna.
    """
    if endpoint is None:
        endpoint = os.getenv('AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT')
    if key is None:
        key = os.getenv('AZURE_DOCUMENT_INTELLIGENCE_KEY')
    
    if not endpoint or not key:
        return {
            'content': '',
            'confidence': 0.0,
            'page_count': 0,
            'success': False,
            'error': 'Missing Azure credentials'
        }
    
    client = AsyncDocumentIntelligenceClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(key),
    )
    
    try:
        async with client:
            poller = await client.begin_analyze_document(
                model_id,
                file_bytes,
                content_type="application/pdf"
            )
            
            analyze_result = await poller.result()
            
            content = analyze_result.content if hasattr(analyze_result, 'content') else ""
            
            confidences = []
            
            if hasattr(analyze_result, 'pages'):
                for page in analyze_result.pages:
                    if hasattr(page, 'words'):
                        for word in page.words:
                            if hasattr(word, 'confidence'):
                                confidences.append(word.confidence)
            
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
            page_count = len(analyze_result.pages) if hasattr(analyze_result, 'pages') else 0
            
            return {
                'content': content,
                'confidence': round(avg_confidence, 4),
                'page_count': page_count,
                'success': True,
                'error': None
            }
            
    except Exception as e:
        return {
            'content': '',
            'confidence': 0.0,
            'page_count': 0,
            'success': False,
            'error': str(e)
        }


def analyze_pdf_from_bytes_sync(
    file_bytes: bytes,
    endpoint: str = None,
    key: str = None,
    model_id: str = "prebuilt-read"
) -> dict:
    """
    Analizuje dokument PDF z bytes i zwraca wyekstraktowana zawartosc.
    Wersja synchroniczna.
    """
    if endpoint is None:
        endpoint = os.getenv('AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT')
    if key is None:
        key = os.getenv('AZURE_DOCUMENT_INTELLIGENCE_KEY')
    
    if not endpoint or not key:
        return {
            'content': '',
            'confidence': 0.0,
            'page_count': 0,
            'success': False,
            'error': 'Missing Azure credentials'
        }
    
    client = DocumentIntelligenceClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(key),
    )
    
    try:
        poller = client.begin_analyze_document(
            model_id,
            file_bytes,
            content_type="application/pdf"
        )
        
        analyze_result = poller.result()
        
        content = analyze_result.content if hasattr(analyze_result, 'content') else ""
        
        confidences = []
        
        if hasattr(analyze_result, 'pages'):
            for page in analyze_result.pages:
                if hasattr(page, 'words'):
                    for word in page.words:
                        if hasattr(word, 'confidence'):
                            confidences.append(word.confidence)
        
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        page_count = len(analyze_result.pages) if hasattr(analyze_result, 'pages') else 0
        
        return {
            'content': content,
            'confidence': round(avg_confidence, 4),
            'page_count': page_count,
            'success': True,
            'error': None
        }
        
    except Exception as e:
        import traceback
        return {
            'content': '',
            'confidence': 0.0,
            'page_count': 0,
            'success': False,
            'error': f"{str(e)}\n{traceback.format_exc()}"
        }


async def analyze_document_file(
    file_path: str,
    endpoint: str = None,
    key: str = None,
    model_id: str = "prebuilt-read"
) -> dict:
    """Analizuje dokument z podanej sciezki pliku"""
    try:
        with open(file_path, 'rb') as f:
            file_bytes = f.read()
        
        return await analyze_pdf_from_bytes(file_bytes, endpoint, key, model_id)
    
    except FileNotFoundError:
        return {
            'content': '',
            'confidence': 0.0,
            'page_count': 0,
            'success': False,
            'error': f'File not found: {file_path}'
        }
    except Exception as e:
        return {
            'content': '',
            'confidence': 0.0,
            'page_count': 0,
            'success': False,
            'error': str(e)
        }


def validate_pdf_bytes(file_bytes: bytes) -> Tuple[bool, str]:
    """Sprawdza czy bytes reprezentuja poprawny PDF"""
    if not file_bytes:
        return False, "Plik jest pusty"
    
    if not file_bytes.startswith(b'%PDF-'):
        return False, "Plik nie jest poprawnym PDF (brak naglowka %PDF-)"
    
    if len(file_bytes) < 1024:
        return False, "Plik PDF jest zbyt maly (< 1KB)"
    
    return True, ""


def extract_key_info_from_text(text: str) -> dict:
    """Ekstraktuje kluczowe informacje z tekstu wypadkowego"""
    import re
    
    info = {
        'has_date': False,
        'has_pesel': False,
        'has_nip': False,
        'dates': [],
        'pesels': [],
        'nips': []
    }
    
    date_patterns = [
        r'\b\d{2}[-./]\d{2}[-./]\d{4}\b',
        r'\b\d{4}[-./]\d{2}[-./]\d{2}\b'
    ]
    for pattern in date_patterns:
        dates = re.findall(pattern, text)
        if dates:
            info['dates'].extend(dates)
            info['has_date'] = True
    
    pesel_pattern = r'\b\d{11}\b'
    pesels = re.findall(pesel_pattern, text)
    if pesels:
        info['pesels'] = pesels
        info['has_pesel'] = True
    
    nip_pattern = r'\b\d{3}[-\s]?\d{3}[-\s]?\d{2}[-\s]?\d{2}\b'
    nips = re.findall(nip_pattern, text)
    if nips:
        info['nips'] = nips
        info['has_nip'] = True
    
    return info


def get_azure_credentials() -> Tuple[str, str]:
    """Pobiera credentials Azure z zmiennych srodowiskowych"""
    endpoint = os.getenv('AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT')
    key = os.getenv('AZURE_DOCUMENT_INTELLIGENCE_KEY')
    
    if not endpoint or not key:
        raise ValueError(
            "Missing Azure credentials. Set AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT "
            "and AZURE_DOCUMENT_INTELLIGENCE_KEY environment variables."
        )
    
    return endpoint, key
