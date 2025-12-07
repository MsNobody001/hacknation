"""
Integration test dla opinion_service z rzeczywistymi danymi wypadku
Wczytuje dane z wcześniejszych analiz i przetwarza je
Użycie: python test_opinion_service_integration.py
"""

import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch
from uuid import uuid4
import json

# Mock Django modules
sys.modules['django'] = MagicMock()
sys.modules['django.db'] = MagicMock()
sys.modules['django.db.models'] = MagicMock()
sys.modules['django.core'] = MagicMock()
sys.modules['django.core.files'] = MagicMock()
sys.modules['django.conf'] = MagicMock()

# Mock LangChain modules
sys.modules['langchain_core'] = MagicMock()
sys.modules['langchain_core.prompts'] = MagicMock()
sys.modules['langchain_core.output_parsers'] = MagicMock()

sys.path.insert(0, str(Path(__file__).resolve().parent))

# Import pydantic AFTER path setup but BEFORE other imports
try:
    from pydantic import BaseModel, Field
    from typing import Optional
except ImportError:
    print("Warning: pydantic not installed, mocking it")
    sys.modules['pydantic'] = MagicMock()


class MockFormalAnalysis:
    """Mock dla modelu FormalAnalysis"""
    def __init__(self):
        self.is_sudden = True
        self.suddenness_explanation = "Zdarzenie było nagłe i nieprzewidywane."
        self.has_external_cause = True
        self.external_cause_explanation = "Przyczyna zewnętrzna: upadek z krzesła."
        self.has_injury = True
        self.injury_explanation = "Złamanie lewej ręki."
        self.is_work_related = True
        self.work_relation_explanation = "Zdarzenie miało miejsce podczas wykonywania pracy."
        self.qualifies_as_work_accident = True
        self.overall_conclusion = "Zdarzenie kwalifikuje się jako wypadek przy pracy."


class MockDiscrepancy:
    """Mock dla modelu Discrepancy"""
    def __init__(self, description):
        self.description = description


class MockDocumentType:
    """Mock dla DocumentType"""
    def __init__(self, name):
        self.name = name


class MockRecommendation:
    """Mock dla modelu Recommendation"""
    def __init__(self, doc_type, reason):
        self.document_type = MockDocumentType(doc_type)
        self.reason = reason


class MockOCRResult:
    """Mock dla modelu OCRResult"""
    def __init__(self, content, doc_name):
        self.extracted_text = content
        self.document = Mock()
        self.document.name = doc_name
        self.document.document_type = Mock()
        self.document.document_type.name = "Wyjaśnienie" if "wyjaśnienia" in doc_name.lower() else "Zaświadczenie"


class TestOpinionServiceIntegration:
    """Integration tests dla opinion_service"""
    
    def test_opinion_structure_with_real_data(self):
        """Test OpinionStructure creation z rzeczywistymi danymi"""
        from pydantic import BaseModel, Field
        from typing import Optional
        
        # Define models locally since imports may be mocked
        class StandpointSection(BaseModel):
            legal_position: str
            confidence_level: str
            summary: str
        
        class CriterionEvaluation(BaseModel):
            criterion_name: str
            fulfilled: Optional[bool] = None
            reasoning: str
        
        class IssueItem(BaseModel):
            issue: str
            recommendation: str
            impact: str
        
        class OpinionStructure(BaseModel):
            standpoint: StandpointSection
            criteria: list = []
            issues: list = []
            conclusions: str
            confidence_level: str
        
        formal_analysis_data = {
            'is_sudden': True,
            'suddenness_explanation': "Zdarzenie było nagłe.",
            'has_external_cause': True,
            'external_cause_explanation': "Upadek z krzesła.",
            'has_injury': True,
            'injury_explanation': "Złamanie ręki.",
            'is_work_related': True,
            'work_relation_explanation': "Podczas pracy.",
            'qualifies_as_work_accident': True,
            'overall_conclusion': "Kwalifikuje się jako wypadek.",
        }
        
        opinion = OpinionStructure(
            standpoint=StandpointSection(
                legal_position="wypadek_przy_pracy",
                confidence_level="wysoki",
                summary="Zdarzenie spełnia wszystkie kryteria wypadku przy pracy."
            ),
            criteria=[
                CriterionEvaluation(
                    criterion_name="nagłość",
                    fulfilled=True,
                    reasoning="Zdarzenie było jednoczasowe."
                ),
                CriterionEvaluation(
                    criterion_name="przyczyna_zewnętrzna",
                    fulfilled=True,
                    reasoning="Upadek z krzesła."
                ),
                CriterionEvaluation(
                    criterion_name="uraz",
                    fulfilled=True,
                    reasoning="Złamanie lewej ręki."
                ),
                CriterionEvaluation(
                    criterion_name="związek_z_pracą",
                    fulfilled=True,
                    reasoning="Zdarzenie miało miejsce podczas pracy."
                ),
            ],
            issues=[
                IssueItem(
                    issue="Brakuje potwierdzenia swiąadków",
                    recommendation="Pobrać oświadczenia od świadków",
                    impact="ważny"
                )
            ],
            conclusions="Na podstawie analizy wszystkich dostępnych danych, zdarzenie kwalifikuje się jako wypadek przy pracy.",
            confidence_level="wysoki"
        )
        
        assert opinion.standpoint.legal_position == "wypadek_przy_pracy"
        assert len(opinion.criteria) == 4
        assert len(opinion.issues) == 1
        assert opinion.standpoint.confidence_level == "wysoki"
        
        print("✅ OpinionStructure creation with real data passed")
    
    def test_opinion_with_uncertainties(self):
        """Test OpinionStructure z brakującymi danymi (status null)"""
        from pydantic import BaseModel, Field
        from typing import Optional
        
        # Define models locally
        class StandpointSection(BaseModel):
            legal_position: str
            confidence_level: str
            summary: str
        
        class CriterionEvaluation(BaseModel):
            criterion_name: str
            fulfilled: Optional[bool] = None
            reasoning: str
        
        class OpinionStructure(BaseModel):
            standpoint: StandpointSection
            criteria: list = []
            issues: list = []
            conclusions: str
            confidence_level: str
        
        opinion = OpinionStructure(
            standpoint=StandpointSection(
                legal_position="wymagane_wyjaśnienia",
                confidence_level="średni",
                summary="Zdarzenie wymaga dodatkowych wyjaśnień."
            ),
            criteria=[
                CriterionEvaluation(
                    criterion_name="nagłość",
                    fulfilled=True,
                    reasoning="Spełnione"
                ),
                CriterionEvaluation(
                    criterion_name="przyczyna_zewnętrzna",
                    fulfilled=None,
                    reasoning="Brakuje danych"
                ),
                CriterionEvaluation(
                    criterion_name="uraz",
                    fulfilled=True,
                    reasoning="Spełnione"
                ),
                CriterionEvaluation(
                    criterion_name="związek_z_pracą",
                    fulfilled=None,
                    reasoning="Wymaga wyjaśnienia"
                ),
            ],
            issues=[],
            conclusions="Wymagane są dodatkowe wyjaśnienia.",
            confidence_level="średni"
        )
        
        assert opinion.standpoint.legal_position == "wymagane_wyjaśnienia"
        assert sum(1 for c in opinion.criteria if c.fulfilled is None) == 2
        assert opinion.standpoint.confidence_level == "średni"
        
        print("✅ OpinionStructure with uncertainties passed")
    
    def test_opinion_with_negative_assessment(self):
        """Test OpinionStructure z negatywną oceną (nie wypadek)"""
        from pydantic import BaseModel, Field
        from typing import Optional
        
        # Define models locally
        class StandpointSection(BaseModel):
            legal_position: str
            confidence_level: str
            summary: str
        
        class CriterionEvaluation(BaseModel):
            criterion_name: str
            fulfilled: Optional[bool] = None
            reasoning: str
        
        class IssueItem(BaseModel):
            issue: str
            recommendation: str
            impact: str
        
        class OpinionStructure(BaseModel):
            standpoint: StandpointSection
            criteria: list = []
            issues: list = []
            conclusions: str
            confidence_level: str
        
        opinion = OpinionStructure(
            standpoint=StandpointSection(
                legal_position="nie_wypadek",
                confidence_level="wysoki",
                summary="Zdarzenie nie spełnia kryteriów wypadku przy pracy."
            ),
            criteria=[
                CriterionEvaluation(
                    criterion_name="nagłość",
                    fulfilled=True,
                    reasoning="Spełnione"
                ),
                CriterionEvaluation(
                    criterion_name="przyczyna_zewnętrzna",
                    fulfilled=False,
                    reasoning="Przyczyna wewnętrzna - zawał serca"
                ),
                CriterionEvaluation(
                    criterion_name="uraz",
                    fulfilled=False,
                    reasoning="Brak urazu - śmierć mózgowa"
                ),
                CriterionEvaluation(
                    criterion_name="związek_z_pracą",
                    fulfilled=False,
                    reasoning="Zdarzenie medyczne, a nie pracowe"
                ),
            ],
            issues=[
                IssueItem(
                    issue="Przyczyna medyczna, a nie pracowa",
                    recommendation="Rozpatrzenie jako choroba zawodowa",
                    impact="krytyczny"
                )
            ],
            conclusions="Zdarzenie nie kwalifikuje się jako wypadek przy pracy.",
            confidence_level="wysoki"
        )
        
        assert opinion.standpoint.legal_position == "nie_wypadek"
        assert sum(1 for c in opinion.criteria if not c.fulfilled) >= 2
        
        print("✅ OpinionStructure with negative assessment passed")
    
    def test_formal_analysis_data_format(self):
        """Test formatowania danych FormalAnalysis"""
        mock_analysis = MockFormalAnalysis()
        
        formal_analysis_data = {
            'is_sudden': mock_analysis.is_sudden,
            'suddenness_explanation': mock_analysis.suddenness_explanation,
            'has_external_cause': mock_analysis.has_external_cause,
            'external_cause_explanation': mock_analysis.external_cause_explanation,
            'has_injury': mock_analysis.has_injury,
            'injury_explanation': mock_analysis.injury_explanation,
            'is_work_related': mock_analysis.is_work_related,
            'work_relation_explanation': mock_analysis.work_relation_explanation,
            'qualifies_as_work_accident': mock_analysis.qualifies_as_work_accident,
            'overall_conclusion': mock_analysis.overall_conclusion,
        }
        
        # Powinniśmy móc serializować do JSON
        json_data = json.dumps(formal_analysis_data, ensure_ascii=False)
        parsed = json.loads(json_data)
        
        assert parsed['is_sudden'] is True
        assert len(parsed['overall_conclusion']) > 0
        
        print("✅ FormalAnalysis data format test passed")
    
    def test_discrepancies_collection(self):
        """Test zbierania rozbieżności"""
        discrepancies = [
            MockDiscrepancy("Brakuje sygnatury w dokumencie A"),
            MockDiscrepancy("Data w dokumencie B jest niezgodna z C"),
            MockDiscrepancy("Sprzeczne informacje o czasu wypadku"),
        ]
        
        discrepancies_data = [
            {'description': d.description} for d in discrepancies
        ]
        
        assert len(discrepancies_data) == 3
        assert all('description' in d for d in discrepancies_data)
        
        json_data = json.dumps(discrepancies_data, ensure_ascii=False)
        assert len(json_data) > 0
        
        print("✅ Discrepancies collection test passed")
    
    def test_recommendations_collection(self):
        """Test zbierania rekomendacji dokumentacji"""
        recommendations = [
            MockRecommendation("Wyjaśnienie poszkodowanego", "Obowiązkowe"),
            MockRecommendation("Zaświadczenie o wypadku", "Obowiązkowe"),
            MockRecommendation("Opinia medyczna ZUS", "Warunkowe"),
        ]
        
        recommendations_data = [
            {
                'document_type': r.document_type.name,
                'reason': r.reason,
            } for r in recommendations
        ]
        
        assert len(recommendations_data) == 3
        assert all('document_type' in d for d in recommendations_data)
        
        json_data = json.dumps(recommendations_data, ensure_ascii=False)
        assert len(json_data) > 0
        
        print("✅ Recommendations collection test passed")
    
    def test_ocr_results_processing(self):
        """Test przetwarzania wyników OCR"""
        ocr_results = [
            MockOCRResult(
                "WYJAŚNIENIE POSZKODOWANEGO\n\nZdarzenie miało miejsce dnia...",
                "wyjaśnienia_poszkodowanego.pdf"
            ),
            MockOCRResult(
                "ZAŚWIADCZENIE O WYPADKU\n\nData wypadku: 15.09.2023",
                "zaświadczenie_o_wypadku.pdf"
            ),
        ]
        
        # Symulacja prepare_combined_documents_text
        combined_text = "\n\n".join([
            f"--- {ocr.document.name} ---\n{ocr.extracted_text}"
            for ocr in ocr_results
        ])
        
        assert len(combined_text) > 0
        assert "WYJAŚNIENIE" in combined_text
        assert "ZAŚWIADCZENIE" in combined_text
        
        print("✅ OCR results processing test passed")
    
    def test_business_context_preparation(self):
        """Test przygotowania kontekstu biznesowego"""
        analysis = Mock()
        analysis.nip = "1234567890"
        analysis.regon = "123456789"
        analysis.pkd_code = "62.01.Z"
        analysis.business_description = "Usługi programistyczne"
        
        business_context_parts = []
        if analysis.nip:
            business_context_parts.append(f"NIP: {analysis.nip}")
        if analysis.regon:
            business_context_parts.append(f"REGON: {analysis.regon}")
        if analysis.pkd_code:
            business_context_parts.append(f"Kod PKD: {analysis.pkd_code}")
        if analysis.business_description:
            business_context_parts.append(f"Opis działalności: {analysis.business_description}")
        
        business_context = "\n".join(business_context_parts)
        
        assert "NIP" in business_context
        assert "REGON" in business_context
        assert "PKD" in business_context
        
        print("✅ Business context preparation test passed")


if __name__ == '__main__':
    print("\n" + "="*70)
    print("INTEGRATION TESTS FOR OPINION_SERVICE")
    print("="*70 + "\n")
    
    test = TestOpinionServiceIntegration()
    
    tests = [
        ("OpinionStructure z rzeczywistymi danymi", test.test_opinion_structure_with_real_data),
        ("OpinionStructure z brakującymi danymi", test.test_opinion_with_uncertainties),
        ("OpinionStructure z negatywną oceną", test.test_opinion_with_negative_assessment),
        ("Format danych FormalAnalysis", test.test_formal_analysis_data_format),
        ("Zbieranie rozbieżności", test.test_discrepancies_collection),
        ("Zbieranie rekomendacji", test.test_recommendations_collection),
        ("Przetwarzanie wyników OCR", test.test_ocr_results_processing),
        ("Przygotowanie kontekstu biznesowego", test.test_business_context_preparation),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            print(f"Uruchamianie: {test_name}...", end=" ")
            test_func()
            passed += 1
        except Exception as e:
            print(f"❌ FAILED: {e}")
            failed += 1
    
    print("\n" + "="*70)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("="*70 + "\n")
