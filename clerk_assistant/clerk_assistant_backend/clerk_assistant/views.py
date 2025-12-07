from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from django.shortcuts import get_object_or_404
from django.http import FileResponse

from .models import (
    Analysis,
    DocumentType,
    Document,
    FormalAnalysis,
    Opinion,
    DraftDocument
)
from .serializers import (
    AnalysisSerializer,
    DocumentTypeSerializer,
    DocumentSerializer,
    DiscrepancySerializer,
    FormalAnalysisSerializer,
    RecommendationSerializer,
    OpinionSerializer,
    DraftDocumentSerializer
)


class DocumentTypeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    List all available document types.
    GET /api/document-types/
    """
    queryset = DocumentType.objects.all()
    serializer_class = DocumentTypeSerializer


class AnalysisViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    Main Analysis endpoint.
    
    POST /api/analyses/ - Create new analysis
    GET /api/analyses/ - List all analyses
    GET /api/analyses/{id}/ - Retrieve complete analysis with all results
    
    Update and delete operations are disabled.
    """
    queryset = Analysis.objects.all()
    serializer_class = AnalysisSerializer
    
    @action(detail=True, methods=['post'], parser_classes=[MultiPartParser])
    def documents(self, request, pk=None):
        """
        Upload PDF documents to analysis.
        POST /api/analyses/{id}/documents/
        
        Accepts multipart/form-data with PDF files.
        Triggers async processing chain after upload.
        """
        analysis = self.get_object()
        
        files = request.FILES.getlist('files')
        if not files:
            return Response(
                {'error': 'No files provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        non_pdf_files = [f.name for f in files if not f.name.lower().endswith('.pdf')]
        if non_pdf_files:
            return Response(
                {'error': f'The following files are not PDFs: {", ".join(non_pdf_files)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        uploaded_documents = []
        for file in files:
            document = Document.objects.create(
                analysis=analysis,
                file=file,
                filename=file.name,
                file_size=file.size
            )
            uploaded_documents.append(document)
        
        serializer = DocumentSerializer(uploaded_documents, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def processing(self, request, pk=None):
        """
        Start processing pipeline for uploaded documents.
        POST /api/analyses/{id}/processing/
        
        Triggers async Celery task chain and returns 202 Accepted.
        """
        analysis = self.get_object()
        
        if not analysis.documents.exists():
            return Response(
                {'error': 'No documents uploaded yet. Upload documents first.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if analysis.status != "pending":
            return Response(
                {'error': f'Analysis is already {analysis.status}'},
                status=status.HTTP_409_CONFLICT
            )
        
        # Trigger Celery task chain
        from .tasks import run_analysis_pipeline
        task_id = run_analysis_pipeline(str(analysis.id))
        
        status_url = request.build_absolute_uri(
            f'/api/analyses/{analysis.id}/status/'
        )
        
        return Response(
            {
                'message': 'Processing started',
                'analysis_id': str(analysis.id),
                'status': 'processing',
                'task_id': task_id,
                'status_url': status_url
            },
            status=status.HTTP_202_ACCEPTED
        )
    
    @action(detail=True, methods=['get'])
    def status(self, request, pk=None):
        """
        Get lightweight status for polling.
        GET /api/analyses/{id}/status/
        
        Returns only status and progress info without full nested data.
        """
        analysis = self.get_object()
        return Response({
            'id': str(analysis.id),
            'status': analysis.status,
            'created_at': analysis.created_at,
            'updated_at': analysis.updated_at,
            # Progress indicators
            'has_documents': analysis.documents.exists(),
            'has_ocr_results': any(doc.ocr_result for doc in analysis.documents.all() if hasattr(doc, 'ocr_result')),
            'has_discrepancies': analysis.discrepancies.exists(),
            'has_formal_analysis': hasattr(analysis, 'formal_analysis'),
            'has_recommendations': analysis.recommendations.exists(),
            'has_opinion': hasattr(analysis, 'opinion'),
            'has_drafts': analysis.drafts.exists(),
            'error_message': analysis.error_message,
        })
    
    @action(detail=True, methods=['get'])
    def discrepancies(self, request, pk=None):
        """
        Get all discrepancies for an analysis.
        GET /api/analyses/{id}/discrepancies/
        """
        analysis = self.get_object()
        discrepancies = analysis.discrepancies.all()
        serializer = DiscrepancySerializer(discrepancies, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'], url_path='formal-analysis')
    def formal_analysis(self, request, pk=None):
        """
        Get formal analysis (legal evaluation).
        GET /api/analyses/{id}/formal-analysis/
        """
        analysis = self.get_object()
        try:
            formal_analysis = analysis.formal_analysis
            serializer = FormalAnalysisSerializer(formal_analysis)
            return Response(serializer.data)
        except FormalAnalysis.DoesNotExist:
            return Response(
                {'detail': 'Formal analysis not yet available'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['get'])
    def recommendations(self, request, pk=None):
        """
        Get all recommendations for an analysis.
        GET /api/analyses/{id}/recommendations/
        """
        analysis = self.get_object()
        recommendations = analysis.recommendations.all()
        serializer = RecommendationSerializer(recommendations, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def opinion(self, request, pk=None):
        """
        Get final AI opinion.
        GET /api/analyses/{id}/opinion/
        """
        analysis = self.get_object()
        try:
            opinion = analysis.opinion
            serializer = OpinionSerializer(opinion)
            return Response(serializer.data)
        except Opinion.DoesNotExist:
            return Response(
                {'detail': 'Opinion not yet available'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['get'])
    def drafts(self, request, pk=None):
        """
        Get list of draft documents.
        GET /api/analyses/{id}/drafts/
        """
        analysis = self.get_object()
        drafts = analysis.drafts.all()
        serializer = DraftDocumentSerializer(drafts, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'], url_path='drafts/(?P<draft_id>[^/.]+)')
    def draft_download(self, request, pk=None, draft_id=None):
        """
        Download a specific draft document.
        GET /api/analyses/{id}/drafts/{draft_id}/
        """
        analysis = self.get_object()
        draft = get_object_or_404(DraftDocument, id=draft_id, analysis=analysis)
        
        response = FileResponse(draft.file.open('rb'))
        response['Content-Type'] = 'application/pdf' if draft.format == 'pdf' else 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        response['Content-Disposition'] = f'attachment; filename="{analysis.id}_{draft.format}.{draft.format}"'
        return response
