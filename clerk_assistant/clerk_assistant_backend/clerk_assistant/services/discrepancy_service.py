import json
import logging
from typing import Optional

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

from .llm_utils import get_azure_llm, prepare_documents_context

logger = logging.getLogger(__name__)


class ExtractedDocumentData(BaseModel):
    """Structured data extracted from a single document."""
    document_name: str = Field(description="Nazwa dokumentu")
    accident_date: Optional[str] = Field(default=None, description="Data wypadku (format: DD.MM.YYYY)")
    accident_time: Optional[str] = Field(default=None, description="Godzina wypadku (format: HH:MM)")
    accident_location: Optional[str] = Field(default=None, description="Miejsce wypadku - adres lub opis lokalizacji")
    workplace_name: Optional[str] = Field(default=None, description="Nazwa zakładu pracy")
    
    # Victim data
    victim_name: Optional[str] = Field(default=None, description="Imię i nazwisko poszkodowanego")
    victim_pesel: Optional[str] = Field(default=None, description="PESEL poszkodowanego")
    victim_address: Optional[str] = Field(default=None, description="Adres zamieszkania poszkodowanego")
    victim_position: Optional[str] = Field(default=None, description="Stanowisko poszkodowanego")
    
    # Witnesses
    witnesses: list[str] = Field(default_factory=list, description="Lista świadków (imiona i nazwiska)")
    
    # Accident details
    circumstances: Optional[str] = Field(default=None, description="Opis okoliczności wypadku")
    causes: Optional[str] = Field(default=None, description="Przyczyny wypadku")
    injuries: Optional[str] = Field(default=None, description="Opis obrażeń")
    
    # Employer data
    employer_name: Optional[str] = Field(default=None, description="Nazwa pracodawcy")
    employer_nip: Optional[str] = Field(default=None, description="NIP pracodawcy")


class DiscrepancyItem(BaseModel):
    """Single discrepancy found between documents."""
    field_name: str = Field(description="Nazwa pola z rozbieżnością (np. accident_date, victim_name)")
    description: str = Field(description="Szczegółowy opis rozbieżności po polsku")
    document_references: list[str] = Field(description="Lista nazw dokumentów zawierających sprzeczne informacje")
    severity: str = Field(description="Waga rozbieżności: critical, major, lub minor")
    conflicting_values: list[str] = Field(description="Lista sprzecznych wartości znalezionych w dokumentach")


class DiscrepancyAnalysisResult(BaseModel):
    """Complete result of discrepancy analysis."""
    discrepancies: list[DiscrepancyItem] = Field(default_factory=list, description="Lista wykrytych rozbieżności")
    analysis_summary: str = Field(description="Podsumowanie przeprowadzonej analizy")
    documents_analyzed: int = Field(description="Liczba przeanalizowanych dokumentów")


EXTRACTION_SYSTEM_PROMPT = """Jesteś ekspertem ds. analizy dokumentacji wypadkowej w Polsce.
Twoim zadaniem jest wyodrębnienie strukturalnych danych z dokumentu wypadkowego.

Wyodrębnij WSZYSTKIE dostępne informacje z dokumentu. Jeśli jakieś pole nie występuje w dokumencie,
pozostaw je puste (null). Bądź precyzyjny - przepisuj dane dokładnie tak jak występują w dokumencie.

Szczególną uwagę zwróć na:
- Daty i godziny (różne formaty zapisu)
- Adresy i lokalizacje
- Dane osobowe (imiona, nazwiska, PESEL)
- Świadków wypadku
- Okoliczności i przyczyny

Odpowiedz TYLKO w formacie JSON zgodnym ze schematem."""

EXTRACTION_USER_PROMPT = """Wyodrębnij dane z poniższego dokumentu:

NAZWA DOKUMENTU: {document_name}
TYP DOKUMENTU: {document_type}

TREŚĆ DOKUMENTU:
{document_content}

Zwróć dane w formacie JSON."""


COMPARISON_SYSTEM_PROMPT = """Jesteś ekspertem ds. analizy dokumentacji wypadkowej w Polsce.
Twoim zadaniem jest porównanie danych wyodrębnionych z wielu dokumentów i wykrycie rozbieżności.

## Kategorie do porównania:

1. **Data i godzina wypadku** - czy wszystkie dokumenty podają tę samą datę i godzinę
2. **Miejsce wypadku** - adres, nazwa zakładu, stanowisko pracy
3. **Dane poszkodowanego** - imię, nazwisko, PESEL, adres, stanowisko
4. **Dane świadków** - czy ci sami świadkowie występują w dokumentach
5. **Okoliczności wypadku** - opis przebiegu zdarzenia
6. **Przyczyny wypadku** - wskazane przyczyny
7. **Obrażenia** - rodzaj i zakres obrażeń

## Klasyfikacja wagi rozbieżności:

- **critical** - rozbieżności w kluczowych danych (data, miejsce, tożsamość poszkodowanego)
  które mogą wpłynąć na uznanie wypadku za wypadek przy pracy
- **major** - rozbieżności w istotnych szczegółach (okoliczności, przyczyny, świadkowie)
- **minor** - drobne różnice (literówki, format zapisu dat, skróty) które nie wpływają na meritum

## Instrukcje:

1. Porównaj każde pole między wszystkimi dokumentami
2. Zidentyfikuj wszelkie różnice, nawet pozornie drobne
3. Oceń wagę każdej rozbieżności
4. Uwzględnij różne formaty zapisu (np. "Jan Kowalski" vs "Kowalski Jan")
5. Zwróć uwagę na brakujące dane w niektórych dokumentach

Myśl krok po kroku i wyjaśnij swoje rozumowanie przed podaniem wyniku.

Odpowiedz TYLKO w formacie JSON zgodnym ze schematem."""

COMPARISON_USER_PROMPT = """Porównaj dane wyodrębnione z {num_documents} dokumentów i wykryj rozbieżności:

{extracted_data_json}

Przeanalizuj krok po kroku:
1. Najpierw wymień wszystkie pola które zawierają dane
2. Dla każdego pola porównaj wartości między dokumentami
3. Zidentyfikuj rozbieżności
4. Oceń wagę każdej rozbieżności

Zwróć wyniki w formacie JSON."""


def _extract_document_data(llm, document: dict) -> ExtractedDocumentData:
    extraction_prompt = ChatPromptTemplate.from_messages([
        ("system", EXTRACTION_SYSTEM_PROMPT),
        ("human", EXTRACTION_USER_PROMPT),
    ])
    
    parser = JsonOutputParser(pydantic_object=ExtractedDocumentData)
    
    chain = extraction_prompt | llm | parser
    
    try:
        result = chain.invoke({
            "document_name": document["document_name"],
            "document_type": document["document_type"],
            "document_content": document["document_content"],
        })
        
        # Ensure document_name is set
        if isinstance(result, dict):
            result["document_name"] = document["document_name"]
            return ExtractedDocumentData(**result)
        
        return result
        
    except Exception as e:
        logger.warning(f"Failed to extract data from {document['document_name']}: {e}")
        # Return minimal data on failure
        return ExtractedDocumentData(document_name=document["document_name"])


def _compare_documents(llm, extracted_data: list[ExtractedDocumentData]) -> DiscrepancyAnalysisResult:
    comparison_prompt = ChatPromptTemplate.from_messages([
        ("system", COMPARISON_SYSTEM_PROMPT),
        ("human", COMPARISON_USER_PROMPT),
    ])
    
    parser = JsonOutputParser(pydantic_object=DiscrepancyAnalysisResult)
    
    chain = comparison_prompt | llm | parser
    
    # Convert extracted data to JSON for the prompt
    extracted_data_json = json.dumps(
        [data.model_dump() for data in extracted_data],
        ensure_ascii=False,
        indent=2
    )
    
    result = chain.invoke({
        "num_documents": len(extracted_data),
        "extracted_data_json": extracted_data_json,
    })
    
    if isinstance(result, dict):
        result["documents_analyzed"] = len(extracted_data)
        return DiscrepancyAnalysisResult(**result)
    
    return result


def _format_discrepancy_description(disc: DiscrepancyItem) -> str:
    # Map severity to Polish
    severity_map = {
        "critical": "KRYTYCZNA",
        "major": "ISTOTNA",
        "minor": "DROBNA"
    }
    severity_pl = severity_map.get(disc.severity.lower(), disc.severity.upper())
    
    # Map field names to Polish descriptions
    field_name_map = {
        "accident_date": "Data wypadku",
        "accident_time": "Godzina wypadku",
        "accident_location": "Miejsce wypadku",
        "workplace_name": "Nazwa zakładu",
        "victim_name": "Imię i nazwisko poszkodowanego",
        "victim_pesel": "PESEL poszkodowanego",
        "victim_address": "Adres poszkodowanego",
        "victim_position": "Stanowisko poszkodowanego",
        "witnesses": "Świadkowie",
        "circumstances": "Okoliczności wypadku",
        "causes": "Przyczyny wypadku",
        "injuries": "Obrażenia",
        "employer_name": "Nazwa pracodawcy",
        "employer_nip": "NIP pracodawcy",
    }
    field_pl = field_name_map.get(disc.field_name, disc.field_name)
    
    # Build formatted description
    parts = [
        f"[{severity_pl}] {disc.description}",
        f"Pole: {field_pl}",
    ]
    
    if disc.document_references:
        parts.append(f"Dokumenty: {', '.join(disc.document_references)}")
    
    if disc.conflicting_values:
        parts.append(f"Sprzeczne wartości: {' ↔ '.join(disc.conflicting_values)}")
    
    return "\n".join(parts)

def detect_discrepancies(analysis_id: str) -> dict:
    from clerk_assistant.models import Analysis, OCRResult, Discrepancy
    
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
            "discrepancies_count": 0
        }
    
    ocr_list = list(ocr_results)
    
    if len(ocr_list) < 2:
        logger.info(f"Only {len(ocr_list)} document(s) in analysis {analysis_id}, "
                   "skipping discrepancy detection")
        return {
            "status": "skipped",
            "message": "At least 2 documents required for discrepancy detection",
            "discrepancies_count": 0
        }
    
    llm = get_azure_llm(temperature=0.1, max_tokens=4096)
    documents = prepare_documents_context(ocr_list)
    
    logger.info(f"Starting discrepancy detection for analysis {analysis_id} "
               f"with {len(documents)} documents")
    
    # Extract structured data from each document
    logger.info("Extracting structured data from documents...")
    extracted_data = []
    for doc in documents:
        logger.debug(f"Extracting data from: {doc['document_name']}")
        data = _extract_document_data(llm, doc)
        extracted_data.append(data)
    
    logger.info(f"Extracted data from {len(extracted_data)} documents")
    
    # Compare extracted data to find discrepancies
    logger.info("Comparing documents for discrepancies...")
    try:
        analysis_result = _compare_documents(llm, extracted_data)
    except Exception as e:
        logger.error(f"Document comparison failed: {e}")
        raise RuntimeError(f"Discrepancy detection failed during comparison: {str(e)}")
    
    # Clear any existing discrepancies for this analysis (in case of re-run)
    Discrepancy.objects.filter(analysis=analysis).delete()

    created_discrepancies = []
    for disc in analysis_result.discrepancies:
        description = _format_discrepancy_description(disc)
        
        discrepancy = Discrepancy.objects.create(
            analysis=analysis,
            description=description
        )
        created_discrepancies.append(discrepancy)
    
    logger.info(f"Detected {len(created_discrepancies)} discrepancies for analysis {analysis_id}")
    
    return {
        "status": "completed",
        "discrepancies_count": len(created_discrepancies),
        "documents_analyzed": analysis_result.documents_analyzed,
        "analysis_summary": analysis_result.analysis_summary,
        "discrepancies": [
            {
                "id": str(d.id),
                "description": d.description
            }
            for d in created_discrepancies
        ]
    }


# Synchronous wrapper for Celery tasks
def detect_discrepancies_sync(analysis_id: str) -> dict:
    return detect_discrepancies(analysis_id)
