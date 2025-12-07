"""
Test dla recommendation_service (documentation requirements analysis)
Użycie: python -m pytest test_recommendation_service.py
lub: python test_recommendation_service.py
"""

import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch, Mock
from uuid import uuid4

# Mock Django modules
sys.modules['django'] = MagicMock()
sys.modules['django.db'] = MagicMock()
sys.modules['django.db.models'] = MagicMock()
sys.modules['django.core'] = MagicMock()
sys.modules['django.core.files'] = MagicMock()
sys.modules['django.conf'] = MagicMock()

import pytest
from pydantic import BaseModel

# Import the service components
sys.path.insert(0, str(Path(__file__).resolve().parent))


class TestDocumentationRequirementsModels:
    """Test Pydantic models for documentation requirements"""
    
    def test_criterion_uncertainty_creation(self):
        from recommendation_service import CriterionUncertainty
        
        uncertainty = CriterionUncertainty(
            criterion_name="nagłość",
            criterion_polish="Nagłość",
            is_uncertain=True,
            uncertainty_description="Brakuje informacji o czasie trwania działania przyczyny",
            required_documents=["Wyjaśnienie poszkodowanego"],
            priority="high"
        )
        
        assert uncertainty.criterion_name == "nagłość"
        assert uncertainty.is_uncertain is True
        assert uncertainty.priority == "high"
    
    def test_medical_opinion_recommendation_creation(self):
        from recommendation_service import MedicalOpinionRecommendation
        
        opinion = MedicalOpinionRecommendation(
            requires_medical_opinion=True,
            reasoning="Uraz wymaga specjalistycznej oceny",
            injury_description="Złamanie ręki",
            urgency="immediate"
        )
        
        assert opinion.requires_medical_opinion is True
        assert opinion.urgency == "immediate"
    
    def test_documentation_requirement_item_creation(self):
        from recommendation_service import DocumentationRequirementItem
        
        doc_req = DocumentationRequirementItem(
            document_type="Wyjaśnienie poszkodowanego",
            reason="Obowiązkowe wyjaśnienie okoliczności wypadku",
            is_mandatory=True,
            context="Formularz do pobrania z ZUS"
        )
        
        assert doc_req.is_mandatory is True
        assert doc_req.document_type == "Wyjaśnienie poszkodowanego"
    
    def test_documentation_requirements_result_creation(self):
        from recommendation_service import (
            DocumentationRequirementsResult,
            DocumentationRequirementItem,
            MedicalOpinionRecommendation,
            CriterionUncertainty
        )
        
        result = DocumentationRequirementsResult(
            mandatory_documents=[
                DocumentationRequirementItem(
                    document_type="Wyjaśnienie poszkodowanego",
                    reason="Obowiązkowe",
                    is_mandatory=True
                )
            ],
            additional_documents=[],
            criterion_uncertainties=[],
            medical_opinion=MedicalOpinionRecommendation(
                requires_medical_opinion=False,
                reasoning="Nie ma wątpliwości co do urazu",
                urgency="optional"
            ),
            summary="Dokumentacja jest kompletna",
            next_steps=[]
        )
        
        assert len(result.mandatory_documents) == 1
        assert result.summary == "Dokumentacja jest kompletna"


class TestPromptLoading:
    """Test loading prompts from files"""
    
    def test_prompts_directory_exists(self):
        prompts_dir = Path(__file__).resolve().parent.parent / 'prompts'
        assert prompts_dir.exists(), f"Prompts directory not found at {prompts_dir}"
    
    def test_system_prompt_file_exists(self):
        prompts_dir = Path(__file__).resolve().parent.parent / 'prompts'
        system_prompt_file = prompts_dir / 'documentation_requirements_system_prompt.txt'
        assert system_prompt_file.exists(), f"System prompt file not found at {system_prompt_file}"
    
    def test_user_prompt_file_exists(self):
        prompts_dir = Path(__file__).resolve().parent.parent / 'prompts'
        user_prompt_file = prompts_dir / 'documentation_requirements_user_prompt.txt'
        assert user_prompt_file.exists(), f"User prompt file not found at {user_prompt_file}"
    
    def test_system_prompt_content_loaded(self):
        from recommendation_service import DOCUMENTATION_REQUIREMENTS_SYSTEM_PROMPT
        
        assert isinstance(DOCUMENTATION_REQUIREMENTS_SYSTEM_PROMPT, str)
        assert len(DOCUMENTATION_REQUIREMENTS_SYSTEM_PROMPT) > 0
        assert "wypadków przy pracy" in DOCUMENTATION_REQUIREMENTS_SYSTEM_PROMPT
    
    def test_user_prompt_content_loaded(self):
        from recommendation_service import DOCUMENTATION_REQUIREMENTS_USER_PROMPT
        
        assert isinstance(DOCUMENTATION_REQUIREMENTS_USER_PROMPT, str)
        assert len(DOCUMENTATION_REQUIREMENTS_USER_PROMPT) > 0
        assert "business_context" in DOCUMENTATION_REQUIREMENTS_USER_PROMPT


class TestAnalyzeDocumentationRequirements:
    """Test documentation requirements analysis function"""
    
    @patch('recommendation_service.get_azure_llm')
    @patch('recommendation_service._analyze_documentation_requirements')
    def test_analyze_documentation_requirements_success(self, mock_analyze, mock_llm):
        """Test successful analysis"""
        from recommendation_service import (
            analyze_documentation_requirements,
            DocumentationRequirementsResult,
            DocumentationRequirementItem,
            MedicalOpinionRecommendation
        )
        
        # Mock the LLM and analysis result
        mock_llm_instance = MagicMock()
        mock_llm.return_value = mock_llm_instance
        
        mock_result = DocumentationRequirementsResult(
            mandatory_documents=[
                DocumentationRequirementItem(
                    document_type="Wyjaśnienie poszkodowanego",
                    reason="Obowiązkowe wyjaśnienie",
                    is_mandatory=True
                ),
                DocumentationRequirementItem(
                    document_type="Zaświadczenie o wypadku",
                    reason="Obowiązkowe zaświadczenie",
                    is_mandatory=True
                )
            ],
            additional_documents=[
                DocumentationRequirementItem(
                    document_type="Dokumenty potwierdzające działalność",
                    reason="Potwierdzenie wykonywania czynności",
                    is_mandatory=False
                )
            ],
            criterion_uncertainties=[],
            medical_opinion=MedicalOpinionRecommendation(
                requires_medical_opinion=False,
                reasoning="Uraz jest jasno udokumentowany",
                urgency="optional"
            ),
            summary="Dokumentacja wymaga uzupełnienia",
            next_steps=["Pozyskać wyjaśnienie od poszkodowanego"]
        )
        
        mock_analyze.return_value = mock_result
        
        # Mock Django models
        with patch('recommendation_service.Analysis') as mock_analysis_model, \
             patch('recommendation_service.OCRResult') as mock_ocr_model, \
             patch('recommendation_service.DocumentType') as mock_doc_type_model, \
             patch('recommendation_service.Recommendation') as mock_rec_model:
            
            # Setup mocks
            mock_analysis = MagicMock()
            mock_analysis.id = str(uuid4())
            mock_analysis.nip = "1234567890"
            mock_analysis.regon = "123456789"
            mock_analysis.pkd_code = "62.01.Z"
            mock_analysis.business_description = "Usługi IT"
            
            mock_analysis_model.objects.get.return_value = mock_analysis
            
            mock_ocr = MagicMock()
            mock_ocr.document.filename = "test.pdf"
            mock_ocr.document.document_type.name = "Zaświadczenie o wypadku"
            mock_ocr.extracted_text = "Tekst testowy"
            
            mock_ocr_model.objects.filter().select_related().exists.return_value = True
            mock_ocr_model.objects.filter().select_related().__iter__ = lambda x: iter([mock_ocr])
            
            mock_doc_type, _ = MagicMock(), MagicMock()
            mock_doc_type_model.objects.get_or_create.return_value = (mock_doc_type, False)
            
            mock_rec_model.objects.create.return_value = MagicMock(id=uuid4())
            
            # Call function
            result = analyze_documentation_requirements(mock_analysis.id)
            
            # Assertions
            assert result['status'] == 'completed'
            assert result['recommendations_count'] == 3
            assert len(result['mandatory_documents']) == 2
            assert len(result['additional_documents']) == 1
    
    @patch('recommendation_service.Analysis')
    def test_analyze_documentation_requirements_not_found(self, mock_analysis_model):
        """Test when analysis not found"""
        from recommendation_service import analyze_documentation_requirements
        
        mock_analysis_model.objects.get.side_effect = Exception("Analysis not found")
        
        with pytest.raises(ValueError):
            analyze_documentation_requirements(str(uuid4()))
    
    @patch('recommendation_service.Analysis')
    def test_analyze_documentation_requirements_no_ocr_results(self, mock_analysis_model):
        """Test when no OCR results available"""
        from recommendation_service import analyze_documentation_requirements
        
        mock_analysis = MagicMock()
        mock_analysis_model.objects.get.return_value = mock_analysis
        
        # Mock OCRResult to return no results
        with patch('recommendation_service.OCRResult') as mock_ocr_model:
            mock_ocr_model.objects.filter().select_related().exists.return_value = False
            
            result = analyze_documentation_requirements(mock_analysis.id)
            
            assert result['status'] == 'skipped'
            assert result['message'] == 'No OCR results available for analysis'


class TestSyncWrapper:
    """Test synchronous wrapper for Celery tasks"""
    
    @patch('recommendation_service.analyze_documentation_requirements')
    def test_analyze_documentation_requirements_sync(self, mock_analyze):
        """Test sync wrapper calls async function"""
        from recommendation_service import analyze_documentation_requirements_sync
        
        test_id = str(uuid4())
        mock_result = {"status": "completed", "recommendations_count": 2}
        mock_analyze.return_value = mock_result
        
        result = analyze_documentation_requirements_sync(test_id)
        
        assert result == mock_result
        mock_analyze.assert_called_once_with(test_id)


class TestLoadPromptFunction:
    """Test _load_prompt utility function"""
    
    def test_load_prompt_file_successfully(self):
        from recommendation_service import _load_prompt
        
        # Test loading system prompt
        content = _load_prompt('documentation_requirements_system_prompt.txt')
        
        assert isinstance(content, str)
        assert len(content) > 0
        assert "wypadków przy pracy" in content
    
    def test_load_prompt_file_not_found(self):
        from recommendation_service import _load_prompt
        
        with pytest.raises(FileNotFoundError):
            _load_prompt('nonexistent_prompt.txt')


# Unit tests without pytest (can be run directly)
def test_models_basic():
    """Basic test without pytest"""
    from recommendation_service import (
        CriterionUncertainty,
        MedicalOpinionRecommendation,
        DocumentationRequirementItem
    )
    
    print("\n=== Testing Models ===\n")
    
    # Test CriterionUncertainty
    uncertainty = CriterionUncertainty(
        criterion_name="nagłość",
        criterion_polish="Nagłość",
        is_uncertain=True,
        uncertainty_description="Test",
        required_documents=["Doc1"],
        priority="high"
    )
    print(f"✓ CriterionUncertainty created: {uncertainty.criterion_polish}")
    
    # Test MedicalOpinionRecommendation
    opinion = MedicalOpinionRecommendation(
        requires_medical_opinion=True,
        reasoning="Test reasoning",
        urgency="immediate"
    )
    print(f"✓ MedicalOpinionRecommendation created: requires={opinion.requires_medical_opinion}")
    
    # Test DocumentationRequirementItem
    doc_req = DocumentationRequirementItem(
        document_type="Test Doc",
        reason="Test reason",
        is_mandatory=True
    )
    print(f"✓ DocumentationRequirementItem created: {doc_req.document_type}")


def test_prompts_basic():
    """Basic test for prompt files without pytest"""
    print("\n=== Testing Prompts ===\n")
    
    prompts_dir = Path(__file__).resolve().parent.parent / 'prompts'
    
    system_prompt_file = prompts_dir / 'documentation_requirements_system_prompt.txt'
    user_prompt_file = prompts_dir / 'documentation_requirements_user_prompt.txt'
    
    if system_prompt_file.exists():
        with open(system_prompt_file, 'r', encoding='utf-8') as f:
            content = f.read()
        print(f"✓ System prompt loaded ({len(content)} chars)")
    else:
        print(f"✗ System prompt not found at {system_prompt_file}")
    
    if user_prompt_file.exists():
        with open(user_prompt_file, 'r', encoding='utf-8') as f:
            content = f.read()
        print(f"✓ User prompt loaded ({len(content)} chars)")
    else:
        print(f"✗ User prompt not found at {user_prompt_file}")


def run_basic_tests():
    """Run basic tests without pytest"""
    print("\n" + "="*60)
    print("RECOMMENDATION SERVICE - BASIC TESTS")
    print("="*60)
    
    try:
        test_models_basic()
        test_prompts_basic()
        
        print("\n" + "="*60)
        print("✓ ALL BASIC TESTS PASSED")
        print("="*60 + "\n")
        return True
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}\n")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_basic_tests()
    sys.exit(0 if success else 1)
