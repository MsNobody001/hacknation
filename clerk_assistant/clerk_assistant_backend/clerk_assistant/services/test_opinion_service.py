"""
Test dla opinion_service (legal opinion generation)
Użycie: python -m pytest test_opinion_service.py -v
lub: python -m pytest test_opinion_service.py::TestOpinionServiceModels -v
"""

import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch, Mock
from uuid import uuid4

# Mock Django modules BEFORE importing anything else
sys.modules['django'] = MagicMock()
sys.modules['django.db'] = MagicMock()
sys.modules['django.db.models'] = MagicMock()
sys.modules['django.core'] = MagicMock()
sys.modules['django.core.files'] = MagicMock()
sys.modules['django.conf'] = MagicMock()

import pytest
from pydantic import BaseModel, Field

# Setup path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent))

# Import Pydantic models directly from opinion_service
# We need to handle the relative import issue
try:
    # First try direct import (when run as module)
    from clerk_assistant.services.opinion_service import (
        StandpointSection,
        CriterionEvaluation,
        IssueItem,
        OpinionStructure,
        _load_prompt,
        _analyze_opinion,
        generate_legal_opinion,
        generate_legal_opinion_sync,
    )
except ImportError:
    # Fallback: import directly from the file (for standalone execution)
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "opinion_service_module",
        Path(__file__).parent / "opinion_service.py"
    )
    opinion_service_module = importlib.util.module_from_spec(spec)
    
    # Mock the relative imports before loading the module
    mock_llm_utils = MagicMock()
    mock_llm_utils.get_azure_llm = MagicMock()
    mock_llm_utils.prepare_combined_documents_text = MagicMock()
    sys.modules['clerk_assistant.services.llm_utils'] = mock_llm_utils
    
    spec.loader.exec_module(opinion_service_module)
    
    StandpointSection = opinion_service_module.StandpointSection
    CriterionEvaluation = opinion_service_module.CriterionEvaluation
    IssueItem = opinion_service_module.IssueItem
    OpinionStructure = opinion_service_module.OpinionStructure
    _load_prompt = opinion_service_module._load_prompt
    _analyze_opinion = opinion_service_module._analyze_opinion
    generate_legal_opinion = opinion_service_module.generate_legal_opinion
    generate_legal_opinion_sync = opinion_service_module.generate_legal_opinion_sync


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
    
    def test_criterion_evaluation_creation(self):
        criterion = CriterionEvaluation(
            criterion_name="nagłość",
            fulfilled=True,
            reasoning="Zdarzenie było jednoczasowe i krótkotrwałe."
        )
        
        assert criterion.criterion_name == "nagłość"
        assert criterion.fulfilled is True
    
    def test_criterion_evaluation_with_null_fulfilled(self):
        criterion = CriterionEvaluation(
            criterion_name="związek_z_pracą",
            fulfilled=None,
            reasoning="Brakuje informacji do oceny."
        )
        
        assert criterion.fulfilled is None
    
    def test_issue_item_creation(self):
        issue = IssueItem(
            issue="Brakuje wyjaśnienia dotyczącego przyczyny urazu",
            recommendation="Pobrać dodatkowe wyjaśnienie od poszkodowanego",
            impact="krytyczny"
        )
        
        assert issue.issue is not None
        assert issue.impact == "krytyczny"
    
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


class TestOpinionServicePrompts:
    """Test prompt loading functionality"""
    
    def test_prompts_directory_exists(self):
        """Verify that prompts directory exists"""
        prompts_dir = Path(__file__).parent.parent / 'prompts'
        assert prompts_dir.exists(), f"Prompts directory not found at {prompts_dir}"
    
    def test_opinion_system_prompt_file_exists(self):
        """Verify that opinion_system_prompt.txt exists"""
        prompts_dir = Path(__file__).parent.parent / 'prompts'
        prompt_file = prompts_dir / 'opinion_system_prompt.txt'
        assert prompt_file.exists(), f"Prompt file not found at {prompt_file}"
    
    def test_opinion_user_prompt_file_exists(self):
        """Verify that opinion_user_prompt.txt exists"""
        prompts_dir = Path(__file__).parent.parent / 'prompts'
        prompt_file = prompts_dir / 'opinion_user_prompt.txt'
        assert prompt_file.exists(), f"Prompt file not found at {prompt_file}"
    
    def test_prompt_file_contents(self):
        """Verify that prompt files have content"""
        prompts_dir = Path(__file__).parent.parent / 'prompts'
        
        system_prompt = (prompts_dir / 'opinion_system_prompt.txt').read_text(encoding='utf-8')
        user_prompt = (prompts_dir / 'opinion_user_prompt.txt').read_text(encoding='utf-8')
        
        assert len(system_prompt) > 0, "System prompt is empty"
        assert len(user_prompt) > 0, "User prompt is empty"
        
        # Verify key phrases
        assert "wypadek" in system_prompt.lower(), "System prompt missing key terms"
        assert "formalna analiza" in user_prompt.lower(), "User prompt missing key terms"


class TestOpinionServiceFunctions:
    """Test main service functions"""
    
    def test_load_prompt_function_exists(self):
        """Verify that _load_prompt function exists and is callable"""
        assert callable(_load_prompt)
    
    def test_analyze_opinion_function_exists(self):
        """Verify that _analyze_opinion function exists and is callable"""
        assert callable(_analyze_opinion)
    
    def test_generate_legal_opinion_function_exists(self):
        """Verify that generate_legal_opinion function exists and is callable"""
        assert callable(generate_legal_opinion)
    
    def test_generate_legal_opinion_sync_function_exists(self):
        """Verify that generate_legal_opinion_sync function exists and is callable"""
        assert callable(generate_legal_opinion_sync)


if __name__ == '__main__':
    # Run tests if executed directly
    pytest.main([__file__, '-v'])
