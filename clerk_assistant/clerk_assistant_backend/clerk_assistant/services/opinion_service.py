import logging
import json
import os
from typing import Optional

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

from .llm_utils import get_azure_llm, prepare_combined_documents_text

logger = logging.getLogger(__name__)


# ============================================================================
# PYDANTIC MODELS - Struktury danych dla opinii prawnej
# ============================================================================

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
# PROMPTY SYSTEMOWE
# ============================================================================

def _load_prompt(filename: str) -> str:
    """
    Wczytaj prompt z pliku tekstowego.
    
    Args:
        filename: Nazwa pliku w katalogu prompts/
        
    Returns:
        Zawartość pliku jako string
    """
    try:
        prompts_dir = os.path.join(os.path.dirname(__file__), '../prompts')
        filepath = os.path.join(prompts_dir, filename)
        with open(filepath, encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        logger.warning(f"Prompt file not found: {filename}, using fallback")
        return ""


# Próba wczytania z pliku, fallback na domyślne prompty
try:
    OPINION_SYSTEM_PROMPT = _load_prompt('opinion_system_prompt.txt')
except Exception:
    OPINION_SYSTEM_PROMPT = """Jesteś doświadczonym ekspertem prawnym specjalizującym się w prawie pracy 
i ubezpieczeniach wypadkowych w Polsce. Twoim zadaniem jest przeanalizowanie zebranych danych 
dotyczących zdarzenia i wydanie kompletnej opinii prawnej na temat kwalifikacji zdarzenia 
jako wypadku przy pracy."""

try:
    OPINION_USER_PROMPT = _load_prompt('opinion_user_prompt.txt')
except Exception:
    OPINION_USER_PROMPT = """Proszę przeanalizować poniższe dane i wydać opinię prawną:
    
## FORMALNA ANALIZA KRYTERIÓW
{formal_analysis_json}

## ROZBIEŻNOŚCI POMIĘDZY DOKUMENTAMI
{discrepancies_json}

## PEŁNE DOKUMENTY
{documents_text}

Na podstawie analizy wydaj opinię w formacie JSON."""


# ============================================================================
# FUNKCJE ANALIZY
# ============================================================================

def _analyze_opinion(
    llm,
    formal_analysis_data: dict,
    discrepancies_data: list,
    recommendations_data: list,
    documents_text: str,
    business_context: str
) -> OpinionStructure:
    """
    Przeprowadź analizę LLM i wygeneruj opinię prawną.
    
    Args:
        llm: Instancja Azure LLM
        formal_analysis_data: Dane z FormalAnalysis
        discrepancies_data: Lista rozbieżności
        recommendations_data: Lista rekomendacji
        documents_text: Połączony tekst wszystkich dokumentów
        business_context: Kontekst biznesowy
        
    Returns:
        OpinionStructure - sparowana struktura opinii
        
    Raises:
        Exception: Jeśli analiza LLM się nie powiedzie
    """
    logger.info("Starting opinion analysis with LLM")
    
    opinion_prompt = ChatPromptTemplate.from_messages([
        ("system", OPINION_SYSTEM_PROMPT),
        ("human", OPINION_USER_PROMPT),
    ])
    
    parser = JsonOutputParser(pydantic_object=OpinionStructure)
    chain = opinion_prompt | llm | parser
    
    # Przygotuj dane do promptu
    formal_analysis_json = json.dumps(formal_analysis_data, ensure_ascii=False, indent=2)
    discrepancies_json = json.dumps(discrepancies_data, ensure_ascii=False, indent=2)
    recommendations_json = json.dumps(recommendations_data, ensure_ascii=False, indent=2)
    
    try:
        result = chain.invoke({
            "formal_analysis_json": formal_analysis_json,
            "discrepancies_json": discrepancies_json,
            "recommendations_json": recommendations_json,
            "documents_text": documents_text,
            "business_context": business_context or "Brak dodatkowego kontekstu",
        })
        
        if isinstance(result, dict):
            return OpinionStructure(**result)
        
        return result
        
    except Exception as e:
        logger.error(f"Opinion analysis failed: {e}")
        raise


# ============================================================================
# GŁÓWNE FUNKCJE SERWISU
# ============================================================================

def generate_legal_opinion(analysis_id: str) -> dict:
    """
    Wygeneruj kompletną opinię prawną na temat wypadku przy pracy.
    
    Proces:
    1. Pobierz Analysis, OCRResult, FormalAnalysis z bazy danych
    2. Pobierz dane z poprzednich analiz (Discrepancy, Recommendation)
    3. Przygotuj kontekst i dokumenty
    4. Wywołaj analizę LLM
    5. Zapisz opinię w modelu Opinion
    6. Zwróć strukturalną odpowiedź
    
    Args:
        analysis_id: UUID identyfikujący Analysis
        
    Returns:
        Dict z wynikami generowania opinii
        
    Raises:
        Analysis.DoesNotExist: Gdy nie znaleziono Analysis
    """
    from clerk_assistant.models import (
        Analysis, OCRResult, FormalAnalysis, 
        Discrepancy, Recommendation, Opinion
    )
    
    logger.info(f"Generating legal opinion for analysis {analysis_id}")
    
    # ========== KROK 1: WALIDACJA I POBRANIE DANYCH ==========
    try:
        analysis = Analysis.objects.get(id=analysis_id)
        logger.info(f"Found analysis: {analysis.id}")
    except Analysis.DoesNotExist:
        logger.error(f"Analysis {analysis_id} not found")
        raise ValueError(f"Analysis {analysis_id} not found")
    
    # Pobierz wyniki OCR
    ocr_results = OCRResult.objects.filter(
        document__analysis=analysis
    ).select_related('document', 'document__document_type')
    
    if not ocr_results.exists():
        logger.warning(f"No OCR results found for analysis {analysis_id}")
        return {
            "status": "skipped",
            "message": "No OCR results available for analysis",
        }
    
    ocr_list = list(ocr_results)
    logger.info(f"Found {len(ocr_list)} OCR results")
    
    # Pobierz FormalAnalysis
    formal_analysis_data = {}
    try:
        formal_analysis = FormalAnalysis.objects.get(analysis=analysis)
        logger.info("Found formal analysis")
        formal_analysis_data = {
            'is_sudden': formal_analysis.is_sudden,
            'suddenness_explanation': formal_analysis.suddenness_explanation,
            'has_external_cause': formal_analysis.has_external_cause,
            'external_cause_explanation': formal_analysis.external_cause_explanation,
            'has_injury': formal_analysis.has_injury,
            'injury_explanation': formal_analysis.injury_explanation,
            'is_work_related': formal_analysis.is_work_related,
            'work_relation_explanation': formal_analysis.work_relation_explanation,
            'qualifies_as_work_accident': formal_analysis.qualifies_as_work_accident,
            'overall_conclusion': formal_analysis.overall_conclusion,
        }
    except FormalAnalysis.DoesNotExist:
        logger.warning(f"No formal analysis found for {analysis_id}")
    
    # ========== KROK 2: POBIERZ DANE Z WCZEŚNIEJSZYCH ANALIZ ==========
    
    # Rozbieżności
    discrepancies = Discrepancy.objects.filter(analysis=analysis)
    discrepancies_data = [
        {'description': d.description} for d in discrepancies
    ]
    logger.info(f"Found {len(discrepancies_data)} discrepancies")
    
    # Rekomendacje
    recommendations = Recommendation.objects.filter(analysis=analysis).select_related('document_type')
    recommendations_data = [
        {
            'document_type': r.document_type.name,
            'reason': r.reason,
        } for r in recommendations
    ]
    logger.info(f"Found {len(recommendations_data)} recommendations")
    
    # ========== KROK 3: PRZYGOTUJ KONTEKST ==========
    
    documents_text = prepare_combined_documents_text(ocr_list)
    logger.info(f"Prepared combined documents text: {len(documents_text)} characters")
    
    # Przygotuj kontekst biznesowy
    business_context_parts = []
    if analysis.nip:
        business_context_parts.append(f"NIP: {analysis.nip}")
    if analysis.regon:
        business_context_parts.append(f"REGON: {analysis.regon}")
    if analysis.pkd_code:
        business_context_parts.append(f"Kod PKD: {analysis.pkd_code}")
    if analysis.business_description:
        business_context_parts.append(f"Opis działalności: {analysis.business_description}")
    
    business_context = "\n".join(business_context_parts) if business_context_parts else None
    
    # ========== KROK 4: INICJUJ LLM I PRZEPROWADŹ ANALIZĘ ==========
    
    llm = get_azure_llm(temperature=0.15, max_tokens=4096)
    logger.info("Initialized Azure LLM with temperature=0.15")
    
    try:
        opinion_result = _analyze_opinion(
            llm,
            formal_analysis_data,
            discrepancies_data,
            recommendations_data,
            documents_text,
            business_context
        )
        logger.info("Opinion analysis completed successfully")
    except Exception as e:
        logger.error(f"Opinion analysis failed: {e}")
        raise RuntimeError(f"Opinion analysis failed: {str(e)}")
    
    # ========== KROK 5: ZAPISZ OPINIĘ W BAZIE ==========
    
    summary = opinion_result.standpoint.summary
    
    detailed_analysis_parts = [
        "=== STANOWISKO ===",
        f"Stanowisko: {opinion_result.standpoint.legal_position}",
        f"Pewność: {opinion_result.standpoint.confidence_level}",
        f"Podsumowanie: {opinion_result.standpoint.summary}",
        "",
        "=== OCENA KRYTERIÓW ===",
    ]
    
    for criterion in opinion_result.criteria:
        status = "SPEŁNIONE" if criterion.fulfilled is True else (
            "NIE SPEŁNIONE" if criterion.fulfilled is False else "NIEOKREŚLONE"
        )
        detailed_analysis_parts.append(
            f"\n{criterion.criterion_name}: {status}\n{criterion.reasoning}"
        )
    
    if opinion_result.issues:
        detailed_analysis_parts.append("\n=== ZIDENTYFIKOWANE PROBLEMY ===\n")
        for issue in opinion_result.issues:
            detailed_analysis_parts.append(
                f"• {issue.issue}\n  Rekomendacja: {issue.recommendation}\n  Wpływ: {issue.impact}"
            )
    
    detailed_analysis_parts.append(f"\n=== WNIOSKI ===\n{opinion_result.conclusions}")
    
    detailed_analysis = "\n".join(detailed_analysis_parts)
    overall_assessment = opinion_result.standpoint.legal_position
    
    # Zapisz lub aktualizuj Opinion
    opinion, created = Opinion.objects.update_or_create(
        analysis=analysis,
        defaults={
            'summary': summary,
            'detailed_analysis': detailed_analysis,
            'overall_assessment': overall_assessment,
        }
    )
    
    logger.info(f"Opinion saved: {'Created' if created else 'Updated'} for analysis {analysis_id}")
    
    # ========== KROK 6: ZWRÓĆ ODPOWIEDŹ ==========
    
    return {
        "status": "success",
        "opinion_id": str(opinion.id),
        "stanowisko": opinion_result.standpoint.legal_position,
        "podsumowanie": opinion_result.standpoint.summary,
        "liczba_kryteriów": len(opinion_result.criteria),
        "liczba_problemów": len(opinion_result.issues),
        "poziom_pewności": opinion_result.standpoint.confidence_level,
        "wnioski": (opinion_result.conclusions[:200] + "..." 
                   if len(opinion_result.conclusions) > 200 
                   else opinion_result.conclusions),
    }


def generate_legal_opinion_sync(analysis_id: str) -> dict:
    """
    Synchroniczny wrapper dla Celery task.
    
    Umożliwia uruchomienie generowania opinii jako zadania asynchronicznego.
    
    Args:
        analysis_id: UUID identyfikujący Analysis
        
    Returns:
        Dict z wynikami
    """
    logger.info(f"Starting sync opinion generation for analysis {analysis_id}")
    
    try:
        result = generate_legal_opinion(analysis_id)
        logger.info(f"Opinion generation completed with status: {result.get('status')}")
        return result
    except Exception as e:
        logger.error(f"Sync opinion generation failed: {e}")
        raise
