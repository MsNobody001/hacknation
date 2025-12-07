"""
OCR Service Agent for Phase 2 - Document Collection and Analysis
"""

import os
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langchain_core.tools import tool
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from django.core.files.base import ContentFile

from clerk_assistant.models import Document, DocumentType, Analysis, OCRResult, Recommendation

from .ocr_utils import (
    analyze_pdf_from_bytes_sync,
    validate_pdf_bytes,
    extract_key_info_from_text,
    get_azure_credentials
)

load_dotenv()

PROMPT_FILE_PATH = "clerk_assistant/prompts/phase2_document_collector.txt"


class AccidentFilesCollectorAgent:
    """Agent AI do zbierania i analizy dokumentow wypadkowych - Faza 2"""
    
    def __init__(self, analysis_id):
        self.llm = AzureChatOpenAI(
            azure_deployment=os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME"),
            openai_api_version=os.environ.get("AZURE_OPENAI_API_VERSION"),
            temperature=0.3,
        )

        try:
            self.analysis = Analysis.objects.get(id=analysis_id)
            self.analysis.status = 'processing'
            self.analysis.save()
        except Analysis.DoesNotExist:
            raise ValueError(f"Analysis with id {analysis_id} does not exist")
        
        self.doc_type_wyjasnienia = DocumentType.objects.get_or_create(
            name="Zapis wyjaśnień poszkodowanego",
            defaults={"description": "Szczegółowe wyjaśnienia poszkodowanego dotyczące okoliczności wypadku"}
        )[0]
        
        self.doc_type_zawadomienie = DocumentType.objects.get_or_create(
            name="Zawiadomienie o wypadku",
            defaults={"description": "Formalne zawiadomienie o zdarzeniu wypadkowym"}
        )[0]

        try:
            self.azure_endpoint, self.azure_key = get_azure_credentials()
        except ValueError as e:
            print(f"Warning: {e}")
            self.azure_endpoint = None
            self.azure_key = None

        @tool
        def process_document_ocr(document_id: str) -> str:
            """Uruchom analize OCR na zapisanym dokumencie"""
            try:
                document = Document.objects.get(id=document_id)
                
                if hasattr(document, 'ocr_result'):
                    return f"Dokument {document.filename} ma juz wynik OCR (pewnosc: {document.ocr_result.confidence_score:.2%})."
                
                if not self.azure_endpoint or not self.azure_key:
                    return "Brak konfiguracji Azure Document Intelligence"
                
                document.file.open('rb')
                file_bytes = document.file.read()
                document.file.close()
                
                is_valid, error_msg = validate_pdf_bytes(file_bytes)
                if not is_valid:
                    return f"Blad walidacji PDF: {error_msg}"
                
                print(f"[OCR] Starting: {document.filename}")
                ocr_result = analyze_pdf_from_bytes_sync(
                    file_bytes=file_bytes,
                    endpoint=self.azure_endpoint,
                    key=self.azure_key,
                    model_id="prebuilt-read"
                )
                
                if not ocr_result['success']:
                    return f"Blad OCR: {ocr_result['error']}"
                
                OCRResult.objects.create(
                    document=document,
                    extracted_text=ocr_result['content'],
                    confidence_score=ocr_result['confidence']
                )
                
                key_info = extract_key_info_from_text(ocr_result['content'])
                
                info_summary = []
                if key_info['has_date']:
                    info_summary.append(f"Wykryto {len(key_info['dates'])} dat")
                if key_info['has_pesel']:
                    info_summary.append(f"Wykryto PESEL")
                if key_info['has_nip']:
                    info_summary.append(f"Wykryto NIP")
                
                stats = (
                    f"OCR zakończony dla: {document.filename}\n"
                    f"  Pewnosc: {ocr_result['confidence']:.2%}\n"
                    f"  Strony: {ocr_result['page_count']}\n"
                    f"  Znakow: {len(ocr_result['content'])}\n"
                )
                
                if info_summary:
                    stats += "  " + ", ".join(info_summary)
                
                return stats
                
            except Document.DoesNotExist:
                return f"Dokument o ID {document_id} nie istnieje"
            except Exception as e:
                return f"Blad podczas OCR: {str(e)}"

        @tool
        def save_wyjasnienia_document(file_content: bytes, filename: str) -> str:
            """Zapisz dokument 'Zapis wyjasnienia poszkodowanego' do bazy danych"""
            try:
                is_valid, error_msg = validate_pdf_bytes(file_content)
                if not is_valid:
                    return f"Blad: {error_msg}"
                
                existing = Document.objects.filter(
                    analysis=self.analysis,
                    document_type=self.doc_type_wyjasnienia
                ).first()
                
                if existing:
                    return f"Dokument wyjasnienia juz istnieje (ID: {existing.id})"
                
                document = Document.objects.create(
                    analysis=self.analysis,
                    document_type=self.doc_type_wyjasnienia,
                    filename=filename,
                    file_size=len(file_content)
                )
                
                document.file.save(filename, ContentFile(file_content), save=True)
                
                if self.azure_endpoint and self.azure_key:
                    ocr_msg = process_document_ocr.invoke({"document_id": str(document.id)})
                    return f"Zapisano dokument wyjasnienia (ID: {document.id}).\n\n{ocr_msg}"
                else:
                    return f"Zapisano dokument wyjasnienia (ID: {document.id}). OCR niedostepny."
                
            except Exception as e:
                return f"Blad podczas zapisu: {str(e)}"

        @tool
        def save_zawadomienie_document(file_content: bytes, filename: str) -> str:
            """Zapisz dokument 'Zawiadomienie o wypadku' do bazy danych"""
            try:
                is_valid, error_msg = validate_pdf_bytes(file_content)
                if not is_valid:
                    return f"Blad: {error_msg}"
                
                existing = Document.objects.filter(
                    analysis=self.analysis,
                    document_type=self.doc_type_zawadomienie
                ).first()
                
                if existing:
                    return f"Dokument zawiadomienia juz istnieje (ID: {existing.id})"
                
                document = Document.objects.create(
                    analysis=self.analysis,
                    document_type=self.doc_type_zawadomienie,
                    filename=filename,
                    file_size=len(file_content)
                )
                
                document.file.save(filename, ContentFile(file_content), save=True)
                
                if self.azure_endpoint and self.azure_key:
                    ocr_msg = process_document_ocr.invoke({"document_id": str(document.id)})
                    return f"Zapisano zawiadomienie (ID: {document.id}).\n\n{ocr_msg}"
                else:
                    return f"Zapisano zawiadomienie (ID: {document.id}). OCR niedostepny."
                
            except Exception as e:
                return f"Blad podczas zapisu: {str(e)}"

        @tool
        def check_documents_completeness() -> str:
            """Sprawdz czy wszystkie wymagane dokumenty zostaly dostarczone"""
            docs = Document.objects.filter(analysis=self.analysis)
            
            status_lines = []
            has_wyjasnienia = False
            has_zawadomienie = False
            wyjasnienia_ocr = False
            zawadomienie_ocr = False
            
            for doc in docs:
                if doc.document_type == self.doc_type_wyjasnienia:
                    has_wyjasnienia = True
                    wyjasnienia_ocr = hasattr(doc, 'ocr_result')
                    status_lines.append(f"Wyjasnienia poszkodowanego - OCR: {'OK' if wyjasnienia_ocr else 'BRAK'}")
                elif doc.document_type == self.doc_type_zawadomienie:
                    has_zawadomienie = True
                    zawadomienie_ocr = hasattr(doc, 'ocr_result')
                    status_lines.append(f"Zawiadomienie o wypadku - OCR: {'OK' if zawadomienie_ocr else 'BRAK'}")
            
            if not has_wyjasnienia:
                status_lines.append("BRAK wyjasnien poszkodowanego")
            if not has_zawadomienie:
                status_lines.append("BRAK zawiadomienia o wypadku")
            
            is_complete = has_wyjasnienia and has_zawadomienie
            ocr_complete = wyjasnienia_ocr and zawadomienie_ocr
            
            result = "Status dokumentacji:\n" + "\n".join(status_lines)
            
            if is_complete and ocr_complete:
                result += "\n\nWszystkie dokumenty dostarczone i przeanalizowane"
            elif is_complete and not ocr_complete:
                result += "\n\nDokumenty dostarczone, OCR niekompletny"
            else:
                result += "\n\nDokumentacja niekompletna"
            
            return result

        @tool
        def request_additional_document(document_type_name: str, reason: str) -> str:
            """Zazadaj dodatkowego dokumentu od uzytkownika"""
            doc_type, _ = DocumentType.objects.get_or_create(
                name=document_type_name,
                defaults={"description": "Dodatkowy dokument wymagany do analizy"}
            )
            
            Recommendation.objects.create(
                analysis=self.analysis,
                document_type=doc_type,
                reason=reason
            )
            
            return f"Zapisano zadanie dokumentu: {document_type_name}\nPowod: {reason}"

        @tool
        def analyze_extracted_texts() -> str:
            """Analizuje wyekstraktowane teksty z dokumentow"""
            docs_with_ocr = Document.objects.filter(
                analysis=self.analysis,
                ocr_result__isnull=False
            )
            
            if docs_with_ocr.count() < 2:
                return "Potrzebuje wynikow OCR z obu dokumentow"
            
            texts = {}
            for doc in docs_with_ocr:
                texts[doc.document_type.name] = {
                    'content': doc.ocr_result.extracted_text,
                    'key_info': extract_key_info_from_text(doc.ocr_result.extracted_text),
                    'confidence': doc.ocr_result.confidence_score
                }
            
            analysis_results = []
            
            if len(texts) >= 2:
                doc_types = list(texts.keys())
                dates1 = set(texts[doc_types[0]]['key_info']['dates'])
                dates2 = set(texts[doc_types[1]]['key_info']['dates'])
                
                common_dates = dates1.intersection(dates2)
                if common_dates:
                    analysis_results.append(f"Wspolne daty: {', '.join(list(common_dates)[:3])}")
            
            for doc_type, data in texts.items():
                analysis_results.append(f"{doc_type}: pewnosc OCR {data['confidence']:.2%}")
            
            return "Analiza tekstow:\n" + "\n".join(analysis_results)

        try:
            with open(PROMPT_FILE_PATH, "r", encoding="utf-8") as file:
                prompt_template = file.read()
        except FileNotFoundError:
            prompt_template = """Jestes ekspertem ZUS ds. obslugi wypadkow przy pracy.
            Analiza ID: {analysis_id}
            NIP: {nip}
            PKD: {pkd_code}
            """
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", prompt_template),
            ("placeholder", "{chat_history}"),
            ("user", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ])
        
        tools = [
            save_wyjasnienia_document,
            save_zawadomienie_document,
            process_document_ocr,
            check_documents_completeness,
            request_additional_document,
            analyze_extracted_texts,
        ]
        
        self.agent = create_tool_calling_agent(self.llm, tools, self.prompt)
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=tools,
            verbose=True,
            max_iterations=15
        )

    def process_documents(self, user_input: str, chat_history=None):
        """Process user input and manage document collection"""
        if chat_history is None:
            chat_history = []
            
        result = self.agent_executor.invoke({
            "input": user_input,
            "chat_history": chat_history,
            "analysis_id": str(self.analysis.id),
            "nip": self.analysis.nip or "nie podano",
            "regon": self.analysis.regon or "nie podano",
            "pkd_code": self.analysis.pkd_code or "nie podano"
        })
        
        return result["output"]
    
    def get_analysis_status(self):
        """Returns current analysis status with OCR info"""
        docs = Document.objects.filter(analysis=self.analysis)
        return {
            "analysis_id": str(self.analysis.id),
            "status": self.analysis.status,
            "documents_count": docs.count(),
            "documents": [
                {
                    "id": str(d.id),
                    "type": d.document_type.name if d.document_type else "Unknown",
                    "filename": d.filename,
                    "has_ocr": hasattr(d, 'ocr_result'),
                    "ocr_confidence": float(d.ocr_result.confidence_score) if hasattr(d, 'ocr_result') else None,
                } for d in docs
            ]
        }
