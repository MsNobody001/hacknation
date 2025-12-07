"""
Standalone unit tests dla opinion_service (legal opinion generation)
Tests pydantic models without requiring full Django/Azure stack
Użycie: python test_opinion_service_standalone.py
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, Mock

# ============================================================================
# INLINE PYDANTIC MODELS (copied from opinion_service.py for testing)
# ============================================================================

from typing import Optional
from pydantic import BaseModel, Field


class StandpointSection(BaseModel):
    """Stanowisko prawne w sprawie wypadku przy pracy."""
    legal_position: str = Field(
        description="Stanowisko prawne: 'wypadek_przy_pracy', 'nie_wypadek', 'wymagane_wyjaśnienia'"
    )
    confidence_level: str = Field(
        description="Poziom pewności: 'wysoki', 'średni', 'niski'"
    )
    summary: str = Field(
        description="Krótkie podsumowanie stanowiska (1-2 zdania)"
    )


class CriterionEvaluation(BaseModel):
    """Ocena spełnienia jednego z kryteriów wypadku przy pracy."""
    criterion_name: str = Field(
        description="Nazwa kryterium: nagłość, przyczyna_zewnętrzna, uraz, związek_z_pracą"
    )
    fulfilled: Optional[bool] = Field(
        default=None,
        description="Czy kryterium jest spełnione: true/false/null (brak danych)"
    )
    reasoning: str = Field(
        description="Szczegółowe uzasadnienie oceny"
    )


class IssueItem(BaseModel):
    """Kwestia wymagająca dalszych działań."""
    issue: str = Field(
        description="Opis problemu lub wątpliwości"
    )
    recommendation: str = Field(
        description="Rekomendowana akcja"
    )
    impact: str = Field(
        description="Wpływ na ostateczną decyzję: 'krytyczny', 'ważny', 'poboczny'"
    )


class OpinionStructure(BaseModel):
    """Kompletna struktura opinii prawnej dotyczącej wypadku przy pracy."""
    standpoint: StandpointSection = Field(
        description="Stanowisko prawne"
    )
    criteria: list[CriterionEvaluation] = Field(
        default_factory=list,
        description="Oceny poszczególnych kryteriów"
    )
    issues: list[IssueItem] = Field(
        default_factory=list,
        description="Zidentyfikowane problemy i wątpliwości"
    )
    conclusions: str = Field(
        description="Wnioski końcowe i rekomendacje"
    )
    confidence_level: str = Field(
        description="Ogólny poziom pewności opinii: 'wysoki', 'średni', 'niski'"
    )


# ============================================================================
# TESTS
# ============================================================================

class TestOpinionServiceModels:
    """Test Pydantic models for opinion service"""
    
    def test_standpoint_section_creation(self):
        standpoint = StandpointSection(
            legal_position="wypadek_przy_pracy",
            confidence_level="wysoki",
            summary="Zdarzenie spełnia wszystkie kryteria wypadku przy pracy."
        )
        
        assert standpoint.legal_position == "wypadek_przy_pracy"
        assert standpoint.confidence_level == "wysoki"
        assert len(standpoint.summary) > 0
        print("✅ test_standpoint_section_creation passed")
    
    def test_criterion_evaluation_creation(self):
        criterion = CriterionEvaluation(
            criterion_name="nagłość",
            fulfilled=True,
            reasoning="Zdarzenie było jednoczasowe i krótkotrwałe."
        )
        
        assert criterion.criterion_name == "nagłość"
        assert criterion.fulfilled is True
        print("✅ test_criterion_evaluation_creation passed")
    
    def test_criterion_evaluation_with_null_fulfilled(self):
        criterion = CriterionEvaluation(
            criterion_name="związek_z_pracą",
            fulfilled=None,
            reasoning="Brakuje informacji do oceny."
        )
        
        assert criterion.fulfilled is None
        print("✅ test_criterion_evaluation_with_null_fulfilled passed")
    
    def test_issue_item_creation(self):
        issue = IssueItem(
            issue="Brakuje wyjaśnienia dotyczącego przyczyny urazu",
            recommendation="Pobrać dodatkowe wyjaśnienie od poszkodowanego",
            impact="krytyczny"
        )
        
        assert issue.issue is not None
        assert issue.impact == "krytyczny"
        print("✅ test_issue_item_creation passed")
    
    def test_opinion_structure_creation(self):
        opinion = OpinionStructure(
            standpoint=StandpointSection(
                legal_position="wypadek_przy_pracy",
                confidence_level="wysoki",
                summary="Test summary"
            ),
            criteria=[
                CriterionEvaluation(
                    criterion_name="nagłość",
                    fulfilled=True,
                    reasoning="Spełnione"
                )
            ],
            issues=[
                IssueItem(
                    issue="Test issue",
                    recommendation="Test recommendation",
                    impact="ważny"
                )
            ],
            conclusions="Test conclusions",
            confidence_level="wysoki"
        )
        
        assert len(opinion.criteria) == 1
        assert len(opinion.issues) == 1
        assert opinion.standpoint.legal_position == "wypadek_przy_pracy"
        print("✅ test_opinion_structure_creation passed")
    
    def test_opinion_with_all_criteria_fulfilled(self):
        """Test opinion where all criteria are fulfilled"""
        opinion = OpinionStructure(
            standpoint=StandpointSection(
                legal_position="wypadek_przy_pracy",
                confidence_level="wysoki",
                summary="Wszystkie kryteria spełnione."
            ),
            criteria=[
                CriterionEvaluation(criterion_name="nagłość", fulfilled=True, reasoning="OK"),
                CriterionEvaluation(criterion_name="przyczyna_zewnętrzna", fulfilled=True, reasoning="OK"),
                CriterionEvaluation(criterion_name="uraz", fulfilled=True, reasoning="OK"),
                CriterionEvaluation(criterion_name="związek_z_pracą", fulfilled=True, reasoning="OK"),
            ],
            issues=[],
            conclusions="Wypadek przy pracy",
            confidence_level="wysoki"
        )
        
        assert all(c.fulfilled is True for c in opinion.criteria)
        assert len(opinion.issues) == 0
        print("✅ test_opinion_with_all_criteria_fulfilled passed")
    
    def test_opinion_with_mixed_criteria(self):
        """Test opinion with mixed fulfilled criteria"""
        opinion = OpinionStructure(
            standpoint=StandpointSection(
                legal_position="wymagane_wyjaśnienia",
                confidence_level="średni",
                summary="Wymaga wyjaśnień."
            ),
            criteria=[
                CriterionEvaluation(criterion_name="nagłość", fulfilled=True, reasoning="OK"),
                CriterionEvaluation(criterion_name="przyczyna_zewnętrzna", fulfilled=None, reasoning="Brak danych"),
                CriterionEvaluation(criterion_name="uraz", fulfilled=True, reasoning="OK"),
                CriterionEvaluation(criterion_name="związek_z_pracą", fulfilled=False, reasoning="Nie spełnione"),
            ],
            issues=[
                IssueItem(issue="Brakuje wyjaśnień", recommendation="Pobrać", impact="krytyczny")
            ],
            conclusions="Wymagane dodatkowe wyjaśnienia",
            confidence_level="średni"
        )
        
        assert sum(1 for c in opinion.criteria if c.fulfilled is True) == 2
        assert sum(1 for c in opinion.criteria if c.fulfilled is False) == 1
        assert sum(1 for c in opinion.criteria if c.fulfilled is None) == 1
        print("✅ test_opinion_with_mixed_criteria passed")
    
    def test_opinion_structure_json_serialization(self):
        """Test that OpinionStructure can be serialized to JSON"""
        import json
        
        opinion = OpinionStructure(
            standpoint=StandpointSection(
                legal_position="wypadek_przy_pracy",
                confidence_level="wysoki",
                summary="Test"
            ),
            criteria=[],
            issues=[],
            conclusions="Test conclusions",
            confidence_level="wysoki"
        )
        
        json_str = json.dumps(opinion.model_dump(), ensure_ascii=False)
        parsed = json.loads(json_str)
        
        assert parsed['standpoint']['legal_position'] == "wypadek_przy_pracy"
        assert 'criteria' in parsed
        print("✅ test_opinion_structure_json_serialization passed")
    
    def test_prompt_files_exist(self):
        """Verify that prompt files exist"""
        prompts_dir = Path(__file__).parent.parent / 'prompts'
        
        system_prompt = prompts_dir / 'opinion_system_prompt.txt'
        user_prompt = prompts_dir / 'opinion_user_prompt.txt'
        
        assert system_prompt.exists(), f"System prompt not found at {system_prompt}"
        assert user_prompt.exists(), f"User prompt not found at {user_prompt}"
        
        # Check they have content
        assert len(system_prompt.read_text()) > 100, "System prompt is too short"
        assert len(user_prompt.read_text()) > 100, "User prompt is too short"
        
        print("✅ test_prompt_files_exist passed")
    
    def test_opinion_service_file_exists(self):
        """Verify that opinion_service.py exists and has content"""
        service_file = Path(__file__).parent / 'opinion_service.py'
        
        assert service_file.exists(), f"opinion_service.py not found at {service_file}"
        content = service_file.read_text()
        
        assert len(content) > 500, "opinion_service.py is too short"
        assert 'generate_legal_opinion' in content, "generate_legal_opinion not found"
        assert 'OpinionStructure' in content, "OpinionStructure not found"
        
        print("✅ test_opinion_service_file_exists passed")


if __name__ == '__main__':
    print("\n" + "="*70)
    print("STANDALONE UNIT TESTS FOR OPINION_SERVICE")
    print("="*70 + "\n")
    
    test = TestOpinionServiceModels()
    
    tests = [
        test.test_standpoint_section_creation,
        test.test_criterion_evaluation_creation,
        test.test_criterion_evaluation_with_null_fulfilled,
        test.test_issue_item_creation,
        test.test_opinion_structure_creation,
        test.test_opinion_with_all_criteria_fulfilled,
        test.test_opinion_with_mixed_criteria,
        test.test_opinion_structure_json_serialization,
        test.test_prompt_files_exist,
        test.test_opinion_service_file_exists,
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"❌ {test_func.__name__} FAILED: {e}")
            failed += 1
    
    print("\n" + "="*70)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("="*70 + "\n")
    
    sys.exit(0 if failed == 0 else 1)
