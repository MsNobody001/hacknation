import logging
from typing import Optional

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

from .llm_utils import get_azure_llm, prepare_combined_documents_text

logger = logging.getLogger(__name__)


class CriterionAnalysis(BaseModel):
    """Analysis of a single work accident criterion."""
    is_fulfilled: Optional[bool] = Field(
        default=None,
        description="Czy kryterium jest spełnione: true/false/null (brak danych)"
    )
    confidence: str = Field(
        default="medium",
        description="Poziom pewności oceny: high, medium, low"
    )
    evidence: list[str] = Field(
        default_factory=list,
        description="Lista cytatów/dowodów z dokumentów potwierdzających ocenę"
    )
    explanation: str = Field(
        description="Szczegółowe uzasadnienie oceny po polsku"
    )
    missing_information: Optional[str] = Field(
        default=None,
        description="Informacje brakujące do pełnej oceny kryterium"
    )


class FormalAnalysisResult(BaseModel):
    """Complete formal analysis result for work accident qualification."""
    
    # 1. Nagłość (Suddenness)
    suddenness: CriterionAnalysis = Field(
        description="Analiza kryterium nagłości zdarzenia"
    )
    
    # 2. Przyczyna zewnętrzna (External Cause)
    external_cause: CriterionAnalysis = Field(
        description="Analiza kryterium przyczyny zewnętrznej"
    )
    
    # 3. Skutek w postaci urazu (Injury Effect)
    injury: CriterionAnalysis = Field(
        description="Analiza kryterium skutku w postaci urazu"
    )
    
    # 4. Związek z pracą (Work Connection)
    work_connection: CriterionAnalysis = Field(
        description="Analiza kryterium związku z pracą"
    )
    
    # Overall conclusion
    qualifies_as_work_accident: Optional[bool] = Field(
        default=None,
        description="Czy zdarzenie kwalifikuje się jako wypadek przy pracy"
    )
    overall_conclusion: str = Field(
        description="Ogólne podsumowanie i wniosek końcowy"
    )
    recommendations: list[str] = Field(
        default_factory=list,
        description="Zalecenia dotyczące uzupełnienia dokumentacji lub dalszych działań"
    )


FORMAL_ANALYSIS_SYSTEM_PROMPT = """Jesteś ekspertem prawnym ds. wypadków przy pracy w Polsce, 
specjalizującym się w ocenie zdarzeń dotyczących osób prowadzących pozarolniczą działalność gospodarczą.

## DEFINICJA WYPADKU PRZY PRACY

Wypadek przy pracy jest zdarzeniem nagłym, spowodowanym przez przyczynę zewnętrzną, która 
doprowadziła do urazu lub śmierci, które nastąpiło w okresie ubezpieczenia wypadkowego 
z tytułu prowadzenia działalności pozarolniczej i podczas wykonywania zwykłych czynności z nią związanych.

**Aby uznać zdarzenie za wypadek przy pracy, MUSZĄ wystąpić WSZYSTKIE 4 elementy:**

### 1. NAGŁOŚĆ ZDARZENIA
Przez nagłość rozumiemy natychmiastowe ujawnienie się przyczyny zewnętrznej lub działanie 
tej przyczyny przez pewien okres, ale **nie dłużej niż przez jedną dniówkę roboczą**.

Przykłady zdarzeń nagłych:
- Wybuch, upadek, zderzenie, porażenie (kilka sekund)
- Działanie hałasu, niskich/wysokich temperatur, promieniowania (do jednej dniówki)
- Kontakt stolarza z piłą tarczową (kilka sekund)
- Oddziaływanie tlenku węgla na palacza kotłów (kilka godzin)

### 2. PRZYCZYNA ZEWNĘTRZNA
O przyczynie zewnętrznej mówimy, gdy do urazu doszło w wyniku oddziaływania na człowieka 
czynnika występującego **poza jego organizmem**.

Przykłady przyczyn zewnętrznych:
- Działanie ruchomych lub ostrych elementów maszyn i urządzeń
- Energia elektryczna
- Ekstremalne temperatury
- Substancje chemiczne powodujące zatrucie
- Spadający przedmiot uderzający człowieka
- Działanie sił natury
- Nietypowe warunki w miejscu pracy (śliska podłoga, porozrzucane przedmioty)

### 3. SKUTEK W POSTACI URAZU
Urazem jest uszkodzenie tkanek ciała lub narządów człowieka wskutek działania czynnika zewnętrznego.

Przykłady urazów:
- Skaleczenie, stłuczenie (uszkodzenie tkanek)
- Zwichnięcie kończyny, wstrząśnienie mózgu (uszkodzenie narządów)
- Złamanie, oparzenie, odmrożenie

### 4. ZWIĄZEK Z PRACĄ
Między wypadkiem a pracą musi zachodzić ścisły związek:
- **Przyczynowy** - praca była przyczyną wypadku
- **Czasowy** - wypadek nastąpił w czasie pracy
- **Miejscowy** - wypadek nastąpił w miejscu pracy
- **Funkcjonalny** - podczas wykonywania zwykłych czynności związanych z prowadzeniem działalności

## INSTRUKCJE ANALIZY

1. Przeanalizuj WSZYSTKIE dostarczone dokumenty
2. Dla KAŻDEGO z 4 kryteriów:
   - Znajdź w dokumentach dowody (cytaty) potwierdzające lub przeczące spełnieniu
   - Oceń czy kryterium jest spełnione (true), niespełnione (false), lub brak danych (null)
   - Określ poziom pewności oceny (high/medium/low)
   - Uzasadnij szczegółowo swoją ocenę
   - Wskaż brakujące informacje jeśli występują

3. Na podstawie analizy wszystkich 4 kryteriów wydaj wniosek końcowy
4. Zaproponuj zalecenia jeśli dokumentacja jest niekompletna

## FORMAT ODPOWIEDZI

Odpowiedz TYLKO w formacie JSON zgodnym ze schematem. Myśl krok po kroku."""

FORMAL_ANALYSIS_USER_PROMPT = """Przeprowadź formalną analizę prawną poniższych dokumentów wypadkowych.
Oceń czy zgłoszone zdarzenie spełnia wszystkie 4 elementy definicji wypadku przy pracy.

KONTEKST DZIAŁALNOŚCI GOSPODARCZEJ:
{business_context}

DOKUMENTY DO ANALIZY:
{documents_text}

Przeanalizuj każde z 4 kryteriów (nagłość, przyczyna zewnętrzna, uraz, związek z pracą) 
i wydaj wniosek końcowy. Zwróć wyniki w formacie JSON."""



def _analyze_documents(llm, documents_text: str, business_context: str) -> FormalAnalysisResult:
    analysis_prompt = ChatPromptTemplate.from_messages([
        ("system", FORMAL_ANALYSIS_SYSTEM_PROMPT),
        ("human", FORMAL_ANALYSIS_USER_PROMPT),
    ])
    
    parser = JsonOutputParser(pydantic_object=FormalAnalysisResult)
    
    chain = analysis_prompt | llm | parser
    
    result = chain.invoke({
        "documents_text": documents_text,
        "business_context": business_context or "Brak dodatkowego kontekstu o działalności gospodarczej.",
    })
    
    if isinstance(result, dict):
        return FormalAnalysisResult(**result)
    
    return result


def perform_formal_analysis(analysis_id: str) -> dict:
    from clerk_assistant.models import Analysis, OCRResult, FormalAnalysis
    
    # Validate analysis exists
    try:
        analysis = Analysis.objects.get(id=analysis_id)
    except Analysis.DoesNotExist:
        logger.error(f"Analysis {analysis_id} not found")
        raise ValueError(f"Analysis {analysis_id} not found")
    
    # Fetch all OCR results for documents in this analysis
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
    
    # Initialize LLM
    llm = get_azure_llm(temperature=0.1, max_tokens=4096)
    
    # Prepare combined document text
    documents_text = prepare_combined_documents_text(ocr_list)
    
    # Prepare business context from Analysis model fields
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
    
    logger.info(f"Starting formal analysis for analysis {analysis_id} "
               f"with {len(ocr_list)} documents")
    
    # Run formal analysis
    try:
        analysis_result = _analyze_documents(llm, documents_text, business_context)
    except Exception as e:
        logger.error(f"Formal analysis failed: {e}")
        raise RuntimeError(f"Formal analysis failed: {str(e)}")
    
    # Delete existing formal analysis if re-running
    FormalAnalysis.objects.filter(analysis=analysis).delete()
    
    # Save formal analysis to database
    formal_analysis = FormalAnalysis.objects.create(
        analysis=analysis,
        
        # Suddenness (Nagłość)
        is_sudden=analysis_result.suddenness.is_fulfilled,
        suddenness_explanation=_format_criterion_explanation(analysis_result.suddenness),
        
        # External Cause (Przyczyna zewnętrzna)
        has_external_cause=analysis_result.external_cause.is_fulfilled,
        external_cause_explanation=_format_criterion_explanation(analysis_result.external_cause),
        
        # Injury (Uraz)
        has_injury=analysis_result.injury.is_fulfilled,
        injury_explanation=_format_criterion_explanation(analysis_result.injury),
        
        # Work Connection (Związek z pracą)
        is_work_related=analysis_result.work_connection.is_fulfilled,
        work_relation_explanation=_format_criterion_explanation(analysis_result.work_connection),
        
        # Conclusion
        qualifies_as_work_accident=analysis_result.qualifies_as_work_accident,
        overall_conclusion=analysis_result.overall_conclusion,
    )
    
    logger.info(f"Formal analysis completed for analysis {analysis_id}: "
               f"qualifies={analysis_result.qualifies_as_work_accident}")
    
    return {
        "status": "completed",
        "formal_analysis_id": str(formal_analysis.id),
        "qualifies_as_work_accident": analysis_result.qualifies_as_work_accident,
        "criteria": {
            "suddenness": {
                "fulfilled": analysis_result.suddenness.is_fulfilled,
                "confidence": analysis_result.suddenness.confidence,
            },
            "external_cause": {
                "fulfilled": analysis_result.external_cause.is_fulfilled,
                "confidence": analysis_result.external_cause.confidence,
            },
            "injury": {
                "fulfilled": analysis_result.injury.is_fulfilled,
                "confidence": analysis_result.injury.confidence,
            },
            "work_connection": {
                "fulfilled": analysis_result.work_connection.is_fulfilled,
                "confidence": analysis_result.work_connection.confidence,
            },
        },
        "overall_conclusion": analysis_result.overall_conclusion,
        "recommendations": analysis_result.recommendations,
    }


def _format_criterion_explanation(criterion: CriterionAnalysis) -> str:
    confidence_map = {
        "high": "wysoka",
        "medium": "średnia",
        "low": "niska"
    }
    confidence_pl = confidence_map.get(criterion.confidence, criterion.confidence)
    
    parts = [
        f"Ocena: {'TAK' if criterion.is_fulfilled else 'NIE' if criterion.is_fulfilled is False else 'BRAK DANYCH'}",
        f"Pewność: {confidence_pl}",
        "",
        "Uzasadnienie:",
        criterion.explanation,
    ]
    
    if criterion.evidence:
        parts.append("")
        parts.append("Dowody z dokumentów:")
        for i, evidence in enumerate(criterion.evidence, 1):
            parts.append(f"  {i}. \"{evidence}\"")
    
    if criterion.missing_information:
        parts.append("")
        parts.append(f"Brakujące informacje: {criterion.missing_information}")
    
    return "\n".join(parts)


# Synchronous wrapper for Celery tasks
def perform_formal_analysis_sync(analysis_id: str) -> dict:
    return perform_formal_analysis(analysis_id)
