"""
Test lokalny dla AccidentFilesCollectorAgent
Użycie: python test_ocr_files_collector.py
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from unittest.mock import MagicMock

sys.modules['django'] = MagicMock()
sys.modules['django.db'] = MagicMock()
sys.modules['django.db.models'] = MagicMock()
sys.modules['django.core'] = MagicMock()
sys.modules['django.core.files'] = MagicMock()
sys.modules['django.core.files.base'] = MagicMock()
sys.modules['django.conf'] = MagicMock()

from dotenv import load_dotenv
load_dotenv()


def find_test_pdf():
    """Znajdz pierwszy dostepny PDF z resources"""
    base = Path(__file__).resolve().parent.parent.parent.parent.parent
    resources = base / "resources" / "karty-wypadku"
    
    if resources.exists():
        for wypadek_dir in sorted(resources.iterdir()):
            if wypadek_dir.is_dir():
                pdfs = list(wypadek_dir.glob("*.pdf"))
                if pdfs:
                    return pdfs[0]
    
    return None


def test_credentials():
    print("\nTest credentials\n")
    
    endpoint = os.getenv('AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT')
    key = os.getenv('AZURE_DOCUMENT_INTELLIGENCE_KEY')
    
    print(f"Endpoint: {'SET' if endpoint else 'MISSING'}")
    print(f"Key: {'SET' if key else 'MISSING'}")
    
    if not (endpoint and key):
        print("Brak credentials w .env")
        return False
    
    return True


def test_ocr():
    print("\nTest OCR z plikiem PDF\n")
    
    test_file = find_test_pdf()
    
    if not test_file:
        print("Brak plikow PDF w resources/karty-wypadku/")
        return False
    
    with open(test_file, 'rb') as f:
        file_bytes = f.read()
    
    print(f"Wczytano: {test_file.name} ({len(file_bytes)} bytes)")
    
    from ocr_utils import (
        analyze_pdf_from_bytes_sync,
        validate_pdf_bytes,
        extract_key_info_from_text
    )
    
    is_valid, error_msg = validate_pdf_bytes(file_bytes)
    if not is_valid:
        print(f"Walidacja FAIL: {error_msg}")
        return False
    
    print("Walidacja OK")
    print("\nUruchamiam OCR...")
    
    result = analyze_pdf_from_bytes_sync(
        file_bytes=file_bytes,
        endpoint=os.getenv('AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT'),
        key=os.getenv('AZURE_DOCUMENT_INTELLIGENCE_KEY')
    )
    
    if result['success']:
        print(f"\nOCR OK")
        print(f"Pewnosc: {result['confidence']:.2%}")
        print(f"Strony: {result['page_count']}")
        print(f"Znakow: {len(result['content'])}")
        
        key_info = extract_key_info_from_text(result['content'])
        print(f"Daty: {len(key_info['dates'])}")
        print(f"PESEL: {len(key_info['pesels'])}")
        print(f"NIP: {len(key_info['nips'])}")
        
        print(f"\nFragment tekstu:")
        print("-" * 60)
        print(result['content'][:300])
        print("-" * 60)
        
        return True
    else:
        print(f"OCR FAIL: {result['error']}")
        return False


def main():
    print("\n" + "="*60)
    print("TEST OCR FILES COLLECTOR AGENT")
    print("="*60)
    
    tests = [
        test_credentials,
        test_ocr,
    ]
    
    results = []
    for test_func in tests:
        try:
            results.append(test_func())
        except Exception as e:
            print(f"\nException: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)
    
    print("\n" + "="*60)
    print("WYNIKI")
    print("="*60)
    
    passed = sum(results)
    total = len(results)
    print(f"{passed}/{total} testow OK")
    
    return all(results)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
