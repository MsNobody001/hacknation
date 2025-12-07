import logging
from typing import Optional

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

from llm_utils import get_azure_llm, prepare_combined_documents_text

logger = logging.getLogger(__name__)

import os

def _load_prompt(filename: str) -> str:
     prompts_dir = os.path.join(os.path.dirname(__file__), '../prompts')
     with open(os.path.join(prompts_dir, filename), encoding='utf-8') as f:
          return f.read()

DOCUMENTATION_REQUIREMENTS_SYSTEM_PROMPT = _load_prompt('documentation_requirements_system_prompt.txt')
DOCUMENTATION_REQUIREMENTS_USER_PROMPT = _load_prompt('documentation_requirements_user_prompt.txt')


class CriterionUncertainty(BaseModel):
    """Uncertainty about a specific work accident criterion."""
    criterion_name: str = Field(
        description="Nazwa kryterium: nagłość, przyczyna_zewnętrzna, uraz, lub związek_z_pracą"
    )
    criterion_polish: str = Field(
        description="Polska nazwa kryterium (Nagłość, Przyczyna zewnętrzna, Uraz, Związek z pracą)"
    )
    is_uncertain: bool = Field(
        description="Czy istnieje wątpliwość dotycząca spełnienia tego kryterium"
    )
    uncertainty_description: str = Field(
        description="Szczegółowy opis wątpliwości lub braku wystarczających informacji"
    )
    required_documents: list[str] = Field(
        default_factory=list,
        description="Lista dokumentów lub informacji wymaganych do wyjaśnienia wątpliwości"
    )
    priority: str = Field(
        description="Priorytet uzupełnienia: high (krytyczne), medium (istotne), low (dodatkowe)"
    )


class MedicalOpinionRecommendation(BaseModel):
    """Recommendation to obtain medical opinion from ZUS."""
    requires_medical_opinion: bool = Field(
        description="Czy konieczna jest opinia Głównego Lekarza Orzecznika ZUS"
    )
    reasoning: str = Field(
        description="Uzasadnienie dla czego opinia medyczna jest konieczna"
    )
    injury_description: Optional[str] = Field(
        default=None,
        description="Opis urazu który wymaga opinii medycznej"
    )
    urgency: str = Field(
        description="Pilność opinii: immediate (niezwłoczna), standard (rutynowa), optional (fakultatywna)"
    )


class DocumentationRequirementItem(BaseModel):
    """Single documentation requirement."""
    document_type: str = Field(description="Typ dokumentu w języku polskim")
    reason: str = Field(description="Uzasadnienie dlaczego dokument jest wymagany")
    is_mandatory: bool = Field(
        description="Czy dokument jest obowiązkowy do pozyskania"
    )
    context: Optional[str] = Field(
        default=None,
        description="Dodatkowy kontekst lub wskazówki gdzie pozyskać dokument"
    )


class DocumentationRequirementsResult(BaseModel):
    """Complete result of documentation requirements analysis."""
    
    # Required documents that are mandatory
    mandatory_documents: list[DocumentationRequirementItem] = Field(
        default_factory=list,
        description="Dokumenty obowiązkowe które muszą być pozyskane"
    )
    
    # Additional documents based on circumstances
    additional_documents: list[DocumentationRequirementItem] = Field(
        default_factory=list,
        description="Dodatkowe dokumenty w zależności od okoliczności wypadku"
    )
    
    # Uncertainties about specific criteria
    criterion_uncertainties: list[CriterionUncertainty] = Field(
        default_factory=list,
        description="Wątpliwości dotycząca poszczególnych kryteriów wypadku"
    )
    
    # Medical opinion recommendation
    medical_opinion: MedicalOpinionRecommendation = Field(
        description="Rekomendacja dotycząca opinii Głównego Lekarza Orzecznika ZUS"
    )
    
    # Summary
    summary: str = Field(
        description="Podsumowanie i ogólne wnioski dotyczące dokumentacji"
    )
    
    next_steps: list[str] = Field(
        default_factory=list,
        description="Zalecane kroki do podjęcia w celu uzupełnienia dokumentacji"
    )




def _analyze_documentation_requirements(llm, documents_text: str, business_context: str) -> DocumentationRequirementsResult:
    analysis_prompt = ChatPromptTemplate.from_messages([
        ("system", DOCUMENTATION_REQUIREMENTS_SYSTEM_PROMPT),
        ("human", DOCUMENTATION_REQUIREMENTS_USER_PROMPT),
    ])
    
    parser = JsonOutputParser(pydantic_object=DocumentationRequirementsResult)
    
    chain = analysis_prompt | llm | parser
    
    result = chain.invoke({
        "documents_text": documents_text,
        "business_context": business_context or "Brak dodatkowego kontekstu o działalności gospodarczej.",
    })
    
    if isinstance(result, dict):
        return DocumentationRequirementsResult(**result)
    
    return result


def analyze_documentation_requirements(analysis_id: str) -> dict:
    from clerk_assistant.models import Analysis, OCRResult, Recommendation, DocumentType
    
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
            "recommendations_count": 0
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
    
    logger.info(f"Starting documentation requirements analysis for analysis {analysis_id} "
               f"with {len(ocr_list)} documents")
    
    # Run documentation requirements analysis
    try:
        analysis_result = _analyze_documentation_requirements(llm, documents_text, business_context)
    except Exception as e:
        logger.error(f"Documentation requirements analysis failed: {e}")
        raise RuntimeError(f"Documentation requirements analysis failed: {str(e)}")
    
    # Clear any existing recommendations for this analysis (in case of re-run)
    Recommendation.objects.filter(analysis=analysis).delete()
    
    # Save all recommendations (both mandatory and additional documents)
    created_recommendations = []
    
    # Process mandatory documents
    for doc_req in analysis_result.mandatory_documents:
        # Get or create DocumentType
        doc_type, _ = DocumentType.objects.get_or_create(
            name=doc_req.document_type,
            defaults={"description": ""}
        )
        
        reason = f"[OBOWIĄZKOWE] {doc_req.reason}"
        if doc_req.context:
            reason += f"\n\nKontekst: {doc_req.context}"
        
        recommendation = Recommendation.objects.create(
            analysis=analysis,
            document_type=doc_type,
            reason=reason
        )
        created_recommendations.append(recommendation)
        logger.debug(f"Created mandatory recommendation for {doc_type.name}")
    
    # Process additional documents
    for doc_req in analysis_result.additional_documents:
        # Get or create DocumentType
        doc_type, _ = DocumentType.objects.get_or_create(
            name=doc_req.document_type,
            defaults={"description": ""}
        )
        
        reason = f"[DODATKOWE] {doc_req.reason}"
        if doc_req.context:
            reason += f"\n\nKontekst: {doc_req.context}"
        
        recommendation = Recommendation.objects.create(
            analysis=analysis,
            document_type=doc_type,
            reason=reason
        )
        created_recommendations.append(recommendation)
        logger.debug(f"Created additional recommendation for {doc_type.name}")
    
    # Format uncertainties for logging
    uncertainties_summary = []
    for uncertainty in analysis_result.criterion_uncertainties:
        if uncertainty.is_uncertain:
            uncertainties_summary.append(
                f"{uncertainty.criterion_polish}: {uncertainty.uncertainty_description}"
            )
    
    logger.info(f"Documentation requirements analysis completed for analysis {analysis_id}: "
               f"{len(created_recommendations)} recommendations created")
    
    if uncertainties_summary:
        logger.info(f"Identified uncertainties: {'; '.join(uncertainties_summary)}")
    
    if analysis_result.medical_opinion.requires_medical_opinion:
        logger.info(f"Medical opinion recommended: {analysis_result.medical_opinion.reasoning}")
    
    # Build response
    response = {
        "status": "completed",
        "recommendations_count": len(created_recommendations),
        "mandatory_documents": [
            {
                "document_type": doc.document_type.name,
                "reason": doc.reason
            }
            for doc in created_recommendations[:len(analysis_result.mandatory_documents)]
        ],
        "additional_documents": [
            {
                "document_type": doc.document_type.name,
                "reason": doc.reason
            }
            for doc in created_recommendations[len(analysis_result.mandatory_documents):]
        ],
        "criterion_uncertainties": [
            {
                "criterion": uncertainty.criterion_polish,
                "is_uncertain": uncertainty.is_uncertain,
                "description": uncertainty.uncertainty_description,
                "priority": uncertainty.priority
            }
            for uncertainty in analysis_result.criterion_uncertainties
            if uncertainty.is_uncertain
        ],
        "medical_opinion": {
            "requires_medical_opinion": analysis_result.medical_opinion.requires_medical_opinion,
            "reasoning": analysis_result.medical_opinion.reasoning,
            "urgency": analysis_result.medical_opinion.urgency
        },
        "summary": analysis_result.summary,
        "next_steps": analysis_result.next_steps,
    }
    
    return response


# Synchronous wrapper for Celery tasks
def analyze_documentation_requirements_sync(analysis_id: str) -> dict:
    return analyze_documentation_requirements(analysis_id)
