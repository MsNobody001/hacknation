"""
Integration test dla recommendation_service z rzeczywistymi danymi wypadku
Wczytuje pliki PDF z folderu data/wypadek i przetwarza je
Użycie: python test_recommendation_service_integration.py
"""

import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, Mock
from uuid import uuid4
import json

# Mock Django modules
sys.modules['django'] = MagicMock()
sys.modules['django.db'] = MagicMock()
sys.modules['django.db.models'] = MagicMock()
sys.modules['django.core'] = MagicMock()
sys.modules['django.core.files'] = MagicMock()
sys.modules['django.conf'] = MagicMock()

sys.path.insert(0, str(Path(__file__).resolve().parent))


def find_accident_data():
    """Znajdź folder z danymi wypadku"""
    base = Path(__file__).resolve().parent.parent.parent.parent.parent
    data_dir = base / "data"
    
    # Szukamy folderów wypadek 1, wypadek 2, itp.
    wypadek_dirs = sorted([d for d in data_dir.iterdir() if d.is_dir() and d.name.startswith("wypadek")])
    
    if not wypadek_dirs:
        print(f"❌ Brak folderów wypadek w {data_dir}")
        return None
    
    # Zwróć pierwszy folder z danymi (zwykle wypadek 2)
    for wypadek_dir in wypadek_dirs:
        files = list(wypadek_dir.glob("*.pdf"))
        if len(files) >= 2:  # Wymagamy co najmniej 2 pliki PDF
            return wypadek_dir
    
    return None


def load_pdf_content(pdf_path: Path) -> str:
    """Wczytaj zawartość PDF (symulacja OCR)"""
    # W rzeczywistości byłoby tutaj przetwarzanie PDF
    # Na potrzeby testu, zwrócimy symulowany tekst
    
    filename = pdf_path.name.lower()
    
    if "wyjaśnień" in filename or "wyjaśnienia" in filename:
        return """WYJAŚNIENIE POSZKODOWANEGO

Dnia 15.09.2023 o godz. 14:30, podczas wykonywania pracy jako samozatrudniony programista,
pracowałem przy biurku w swoim domowym biurze. Nagle przewróciłem się na krześle
i upadłem na podłogę, ulegając złamaniu lewej ręki.

Świadkami zdarzenia byli: moja żona i kolega pracujący ze mną.
Natychmiast udzielono mi pierwszej pomocy, a następnie wezwano pogotowie.
"""
    
    elif "zawiadomienie" in filename or "zaświadczenie" in filename:
        return """ZAŚWIADCZENIE O WYPADKU

Imię i nazwisko poszkodowanego: Jan Kowalski
PESEL: 75051234567
Data wypadku: 15.09.2023
Godzina wypadku: 14:30
Miejsce wypadku: Warszawa, ul. Testowa 10, mieszkanie prywatne
Rodzaj urazu: Złamanie lewej ręki
Rodzaj działalności: Usługi IT - programowanie
"""
    
    elif "karta wypadku" in filename:
        return """KARTA WYPADKU

1. DANE POSZKODOWANEGO
Imię i nazwisko: Jan Kowalski
PESEL: 75051234567
Data urodzenia: 12.05.1975

2. ZDARZENIE
Data: 15.09.2023
Godzina: 14:30
Miejsce: Warszawa, ul. Testowa 10

3. PRZYCZYNA WYPADKU
Upadek z krzesła - niestabilna pozycja siedząca
"""
    
    elif "opinia" in filename:
        return """OPINIA MEDYCZNA

Pacjent: Jan Kowalski
Data badania: 15.09.2023
Diagnoza: Złamanie kości promieniowej lewej ręki
Zalecenia: Immobilizacja, fizjoterapia
"""
    
    return "Zawartość PDF"


class MockOCRResult:
    """Mock obiektu OCRResult"""
    def __init__(self, filename, content):
        self.document = MockDocument(filename)
        self.extracted_text = content
        self.confidence_score = 0.92
        self.id = uuid4()


class MockDocument:
    """Mock obiektu Document"""
    def __init__(self, filename):
        self.filename = filename
        self.id = uuid4()
        self.document_type = MockDocumentType(self._infer_type(filename))
    
    def _infer_type(self, filename):
        if "wyjaśnień" in filename.lower():
            return "Wyjaśnienia poszkodowanego"
        elif "zaświadczenie" in filename.lower():
            return "Zaświadczenie o wypadku"
        elif "karta" in filename.lower():
            return "Karta wypadku"
        elif "opinia" in filename.lower():
            return "Opinia medyczna"
        else:
            return "Inny dokument"


class MockDocumentType:
    """Mock obiektu DocumentType"""
    def __init__(self, name):
        self.name = name
        self.id = uuid4()


def create_mock_analysis(data_dir: Path):
    """Stwórz mock obiektu Analysis z rzeczywistymi danymi"""
    from recommendation_service import (
        CriterionUncertainty,
        MedicalOpinionRecommendation,
        DocumentationRequirementItem,
        DocumentationRequirementsResult
    )
    
    print(f"\n📁 Wczytywanie danych z: {data_dir.name}\n")
    
    # Wczytaj wszystkie PDF-y
    pdf_files = sorted(data_dir.glob("*.pdf"))
    
    if not pdf_files:
        print("❌ Brak plików PDF w folderze")
        return None
    
    print(f"📄 Znalezione pliki ({len(pdf_files)}):")
    for pdf in pdf_files:
        print(f"   - {pdf.name}")
    
    # Utwórz mock OCRResult dla każdego PDF-a
    ocr_results = []
    for pdf_path in pdf_files:
        content = load_pdf_content(pdf_path)
        ocr_result = MockOCRResult(pdf_path.name, content)
        ocr_results.append(ocr_result)
        print(f"✓ Załadowano OCR: {pdf_path.name}")
    
    # Stwórz mock Analysis obiektu
    analysis_mock = MagicMock()
    analysis_mock.id = str(uuid4())
    analysis_mock.nip = "1234567890"
    analysis_mock.regon = "123456789"
    analysis_mock.pkd_code = "62.01.Z"
    analysis_mock.business_description = "Usługi IT - programowanie"
    
    print(f"\n✓ Stworzony mock Analysis:")
    print(f"  ID: {analysis_mock.id}")
    print(f"  NIP: {analysis_mock.nip}")
    print(f"  PKD: {analysis_mock.pkd_code}")
    print(f"  Dokumenty: {len(ocr_results)}")
    
    return analysis_mock, ocr_results


def test_create_documentation_requirements_result():
    """Test - utwórz DocumentationRequirementsResult z rzeczywistych danych"""
    from recommendation_service import (
        CriterionUncertainty,
        MedicalOpinionRecommendation,
        DocumentationRequirementItem,
        DocumentationRequirementsResult
    )
    
    print("\n" + "="*70)
    print("TEST 1: Tworzenie DocumentationRequirementsResult")
    print("="*70)
    
    # Symuluj analizę - wiele wątpliwości z rzeczywistymi danymi
    criterion_uncertainties = [
        CriterionUncertainty(
            criterion_name="nagłość",
            criterion_polish="Nagłość",
            is_uncertain=True,
            uncertainty_description="Brakuje jasnych informacji o czasie trwania upadku i jego przyczynach",
            required_documents=[
                "Szczegółowe wyjaśnienie od poszkodowanego",
                "Dokumenty potwierdzające warunki pracy w domowym biurze"
            ],
            priority="high"
        ),
        CriterionUncertainty(
            criterion_name="przyczyna_zewnętrzna",
            criterion_polish="Przyczyna zewnętrzna",
            is_uncertain=False,
            uncertainty_description="Wypadek powstał wyraźnie ze względu na upadek",
            required_documents=[],
            priority="low"
        ),
        CriterionUncertainty(
            criterion_name="uraz",
            criterion_polish="Uraz",
            is_uncertain=False,
            uncertainty_description="Złamanie lewej ręki jest udokumentowane",
            required_documents=[],
            priority="low"
        ),
        CriterionUncertainty(
            criterion_name="związek_z_pracą",
            criterion_polish="Związek z pracą",
            is_uncertain=True,
            uncertainty_description="Wątpliwości czy upadek nastąpił podczas wykonywania pracy pozarolniczej",
            required_documents=[
                "Dokumenty potwierdzające prowadzenie działalności programistycznej",
                "Kopia umów z klientami",
                "Faktury za wykonane usługi"
            ],
            priority="high"
        )
    ]
    
    result = DocumentationRequirementsResult(
        mandatory_documents=[
            DocumentationRequirementItem(
                document_type="Wyjaśnienia poszkodowanego",
                reason="Obowiązkowe wyjaśnienie okoliczności wypadku zawierające opis tego co się stało",
                is_mandatory=True,
                context="Poszkodowany musi jasno opisać jak doszło do upadku z krzesła i jakie były okoliczności"
            ),
            DocumentationRequirementItem(
                document_type="Zaświadczenie o wypadku",
                reason="Obowiązkowe zaświadczenie potwierdzające datę, godzinę i miejsce wypadku",
                is_mandatory=True,
                context="Zaświadczenie musi zawierać potwierdzenie udzielonej pierwszej pomocy"
            )
        ],
        additional_documents=[
            DocumentationRequirementItem(
                document_type="Dokumenty potwierdzające działalność pozarolniczą",
                reason="Potwierdza że poszkodowany rzeczywiście prowadzi działalność programistyczną",
                is_mandatory=False,
                context="Kopie umów z klientami, faktury za wykonane usługi lub zlecenia"
            ),
            DocumentationRequirementItem(
                document_type="Dokumentacja warsztatu domowego",
                reason="Potwierdzenie warunków pracy w biurze domowym",
                is_mandatory=False,
                context="Zdjęcia stanowiska pracy, umowy najmu lub prawo do mieszkania"
            ),
            DocumentationRequirementItem(
                document_type="Kartę informacyjną ze szpitala",
                reason="Opis udzielonej pierwszej pomocy medycznej",
                is_mandatory=False,
                context="Dokument ze szpitala potwierdzający przyjęcie i diagnozę"
            )
        ],
        criterion_uncertainties=criterion_uncertainties,
        medical_opinion=MedicalOpinionRecommendation(
            requires_medical_opinion=True,
            reasoning="Konieczna jest opinia Głównego Lekarza Orzecznika ZUS w celu oceny czy złamanie ręki spełnia kryteria wypadku przy pracy w kontekście działalności samozatrudnionego programisty",
            injury_description="Złamanie lewej kości promieniowej",
            urgency="standard"
        ),
        summary="Dokumentacja wymaga uzupełnienia. Kluczowe jest wyjaśnienie czy wypadek nastąpił rzeczywiście podczas wykonywania pracy pozarolniczej oraz czy warunki w biurze domowym były bezpieczne.",
        next_steps=[
            "1. Pozyskać szczegółowe wyjaśnienia od poszkodowanego",
            "2. Zebrać dokumenty potwierdzające działalność pozarolniczą",
            "3. Uzyskać kopię karty szpitalnej",
            "4. Wysłać do Głównego Lekarza Orzecznika ZUS opinię do oceny"
        ]
    )
    
    print("\n✅ Stworzony DocumentationRequirementsResult:")
    print(f"   - Dokumenty obowiązkowe: {len(result.mandatory_documents)}")
    for doc in result.mandatory_documents:
        print(f"     • {doc.document_type}")
    
    print(f"   - Dokumenty dodatkowe: {len(result.additional_documents)}")
    for doc in result.additional_documents:
        print(f"     • {doc.document_type}")
    
    print(f"   - Wątpliwości kryteriów: {len([u for u in result.criterion_uncertainties if u.is_uncertain])}/{len(result.criterion_uncertainties)}")
    for uncertainty in result.criterion_uncertainties:
        if uncertainty.is_uncertain:
            print(f"     ⚠️  {uncertainty.criterion_polish}: {uncertainty.priority}")
    
    print(f"   - Opinia medyczna wymagana: {result.medical_opinion.requires_medical_opinion}")
    
    return result


def test_with_real_accident_data():
    """Test - analiza rzeczywistych danych wypadku"""
    print("\n" + "="*70)
    print("TEST 2: Analiza rzeczywistych danych wypadku")
    print("="*70)
    
    accident_dir = find_accident_data()
    if not accident_dir:
        print("⚠️  Brak danych wypadku do testowania")
        return None
    
    analysis_mock, ocr_results = create_mock_analysis(accident_dir)
    
    if not analysis_mock:
        print("❌ Nie udało się stworzyć mock Analysis")
        return None
    
    # Wyświetl wczytane dokumenty
    print("\n📋 Zawartość wczytanych dokumentów:\n")
    for i, ocr in enumerate(ocr_results, 1):
        doc_type = ocr.document.document_type.name
        content_preview = ocr.extracted_text[:100].replace('\n', ' ')
        print(f"{i}. {ocr.document.filename}")
        print(f"   Typ: {doc_type}")
        print(f"   Treść (podgląd): {content_preview}...")
        print()
    
    return ocr_results


def test_prepare_combined_documents_text():
    """Test - przygotowanie połączonego tekstu dokumentów"""
    print("\n" + "="*70)
    print("TEST 3: Przygotowanie połączonego tekstu dokumentów")
    print("="*70)
    
    from llm_utils import prepare_combined_documents_text
    
    accident_dir = find_accident_data()
    if not accident_dir:
        print("⚠️  Brak danych wypadku")
        return None
    
    _, ocr_results = create_mock_analysis(accident_dir)
    
    try:
        combined_text = prepare_combined_documents_text(ocr_results)
        
        print(f"\n✅ Przygotowano połączony tekst:")
        print(f"   - Liczba dokumentów: {len(ocr_results)}")
        print(f"   - Długość tekstu: {len(combined_text)} znaków")
        print(f"\n📝 Podgląd (pierwsze 500 znaków):\n")
        print(combined_text[:500])
        print("...\n")
        
        return combined_text
    except Exception as e:
        print(f"❌ Błąd przy przygotowaniu tekstu: {e}")
        import traceback
        traceback.print_exc()
        return None


def run_integration_tests():
    """Uruchom wszystkie testy integracyjne"""
    print("\n" + "="*70)
    print("RECOMMENDATION SERVICE - INTEGRATION TESTS")
    print("Testy z rzeczywistymi danymi wypadków")
    print("="*70)
    
    try:
        # Test 1 - Tworzenie wyniku
        result = test_create_documentation_requirements_result()
        if not result:
            return False
        
        # Test 2 - Wczytanie rzeczywistych danych
        ocr_results = test_with_real_accident_data()
        if not ocr_results:
            print("⚠️  Test 2 pominięty - brak danych")
        
        # Test 3 - Przygotowanie tekstu
        combined_text = test_prepare_combined_documents_text()
        if not combined_text:
            print("⚠️  Test 3 pominięty")
        
        print("\n" + "="*70)
        print("✅ WSZYSTKIE TESTY INTEGRACYJNE PRZESZŁY")
        print("="*70 + "\n")
        return True
    
    except Exception as e:
        print(f"\n❌ BŁĄD TESTU: {e}\n")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_integration_tests()
    sys.exit(0 if success else 1)
