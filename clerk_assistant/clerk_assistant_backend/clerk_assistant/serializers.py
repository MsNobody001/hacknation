from rest_framework import serializers
from .models import (
    DocumentType,
    Analysis,
    Document,
    OCRResult,
    Discrepancy,
    FormalAnalysis,
    Recommendation,
    Opinion,
    DraftDocument
)


class DocumentTypeSerializer(serializers.ModelSerializer):
    """
    Read-only serializer for DocumentType.
    """
    class Meta:
        model = DocumentType
        fields = ['id', 'name', 'description']
        read_only_fields = ['id', 'name', 'description']


class OCRResultSerializer(serializers.ModelSerializer):
    """
    Read-only serializer for OCR results.
    """
    class Meta:
        model = OCRResult
        fields = [
            'id',
            'extracted_text',
            'confidence_score',
            'processed_at'
        ]
        read_only_fields = fields


class DocumentSerializer(serializers.ModelSerializer):
    """
    Read-only serializer for Document with nested OCR result.
    """
    document_type = DocumentTypeSerializer(read_only=True)
    ocr_result = OCRResultSerializer(read_only=True)
    
    class Meta:
        model = Document
        fields = [
            'id',
            'document_type',
            'file',
            'filename',
            'uploaded_at',
            'file_size',
            'ocr_result'
        ]
        read_only_fields = fields


class DiscrepancySerializer(serializers.ModelSerializer):
    """
    Read-only serializer for Discrepancy.
    """
    class Meta:
        model = Discrepancy
        fields = ['id', 'description']
        read_only_fields = fields


class FormalAnalysisSerializer(serializers.ModelSerializer):
    """
    Read-only serializer for FormalAnalysis (legal evaluation).
    """
    class Meta:
        model = FormalAnalysis
        fields = [
            'id',
            'is_sudden',
            'suddenness_explanation',
            'has_external_cause',
            'external_cause_explanation',
            'has_injury',
            'injury_explanation',
            'is_work_related',
            'work_relation_explanation',
            'qualifies_as_work_accident',
            'overall_conclusion',
            'assessed_at'
        ]
        read_only_fields = fields


class RecommendationSerializer(serializers.ModelSerializer):
    """
    Read-only serializer for Recommendation with nested document type.
    """
    document_type = DocumentTypeSerializer(read_only=True)
    
    class Meta:
        model = Recommendation
        fields = [
            'id',
            'document_type',
            'reason',
            'created_at'
        ]
        read_only_fields = fields


class OpinionSerializer(serializers.ModelSerializer):
    """
    Read-only serializer for Opinion.
    """
    class Meta:
        model = Opinion
        fields = [
            'id',
            'summary',
            'detailed_analysis',
            'overall_assessment',
            'generated_at'
        ]
        read_only_fields = fields


class DraftDocumentSerializer(serializers.ModelSerializer):
    """
    Serializer for DraftDocument with writable format field.
    """
    class Meta:
        model = DraftDocument
        fields = [
            'id',
            'format',
            'file',
            'generated_at',
            'file_size'
        ]
        read_only_fields = ['id', 'file', 'generated_at', 'file_size']


class AnalysisSerializer(serializers.ModelSerializer):
    """
    Serializer for Analysis with writable Work Connection fields.
    Includes nested relationships for complete analysis view.
    """
    # Nested read-only relationships
    documents = DocumentSerializer(many=True, read_only=True)
    discrepancies = DiscrepancySerializer(many=True, read_only=True)
    formal_analysis = FormalAnalysisSerializer(read_only=True)
    recommendations = RecommendationSerializer(many=True, read_only=True)
    opinion = OpinionSerializer(read_only=True)
    drafts = DraftDocumentSerializer(many=True, read_only=True)
    
    class Meta:
        model = Analysis
        fields = [
            'id',
            'created_at',
            'updated_at',
            'status',
            'error_message',
            # Writable Work Connection fields
            'nip',
            'regon',
            'pkd_code',
            'business_description',
            # Nested relationships
            'documents',
            'discrepancies',
            'formal_analysis',
            'recommendations',
            'opinion',
            'drafts'
        ]
        read_only_fields = [
            'id',
            'created_at',
            'updated_at',
            'status',
            'error_message',
            'documents',
            'discrepancies',
            'formal_analysis',
            'recommendations',
            'opinion',
            'drafts'
        ]
