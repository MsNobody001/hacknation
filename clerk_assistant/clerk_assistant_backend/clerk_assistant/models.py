from django.db import models
import uuid

class DocumentType(models.Model):
    """
    Types of documents as defined in project requirements.
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']


class Analysis(models.Model):
    """
    Main session. Stores the state of the accident analysis process.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Stores technical failures
    error_message = models.TextField(blank=True, null=True)

    # Context fields required by PDF  to validate "Work Connection"
    # We fetch these from CEIDG/GUS based on user input, then save them here.
    nip = models.CharField(max_length=20, blank=True, null=True)
    regon = models.CharField(max_length=20, blank=True, null=True)
    pkd_code = models.CharField(max_length=10, blank=True, null=True, help_text="Main business activity code")
    business_description = models.TextField(blank=True, help_text="Description of business activities for AI context")

    def __str__(self):
        return f"Analysis {self.id} - {self.status}"
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Analyses'


class Document(models.Model):
    """
    Uploaded PDF documents.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    analysis = models.ForeignKey(Analysis, on_delete=models.CASCADE, related_name='documents')
    document_type = models.ForeignKey(DocumentType, on_delete=models.PROTECT, null=True, blank=True)
    
    file = models.FileField(upload_to='documents/%Y/%m/%d/')
    filename = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file_size = models.IntegerField()
    
    def __str__(self):
        return f"{self.filename} ({self.document_type})"
    
    class Meta:
        ordering = ['uploaded_at']


class OCRResult(models.Model):
    """
    Raw text extracted from scans.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.OneToOneField(Document, on_delete=models.CASCADE, related_name='ocr_result')
    extracted_text = models.TextField()
    confidence_score = models.FloatField(null=True, blank=True)
    processed_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"OCR for {self.document.filename}"


class Discrepancy(models.Model):
    """
    Inconsistencies detected across all documents in the analysis.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    analysis = models.ForeignKey(Analysis, on_delete=models.CASCADE, related_name='discrepancies')
    
    description = models.TextField()
    
    def __str__(self):
        return f"Discrepancy in {self.analysis.id}"
    
    class Meta:
        verbose_name_plural = 'Discrepancies'


class FormalAnalysis(models.Model):
    """
    Legal evaluation of the 4 key elements of an accident.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    analysis = models.OneToOneField(Analysis, on_delete=models.CASCADE, related_name='formal_analysis')
    
    # 1. Nagłość (Suddenness)
    is_sudden = models.BooleanField(null=True, blank=True)
    suddenness_explanation = models.TextField(blank=True)
    
    # 2. Przyczyna zewnętrzna (External cause) 
    has_external_cause = models.BooleanField(null=True, blank=True)
    external_cause_explanation = models.TextField(blank=True)
    
    # 3. Skutek w postaci urazu (Injury effect)
    has_injury = models.BooleanField(null=True, blank=True)
    injury_explanation = models.TextField(blank=True)
    
    # 4. Związek z pracą (Work connection)
    is_work_related = models.BooleanField(null=True, blank=True)
    work_relation_explanation = models.TextField(blank=True)
    
    # Conclusion
    qualifies_as_work_accident = models.BooleanField(null=True, blank=True)
    overall_conclusion = models.TextField()
    
    assessed_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Analysis Result: {self.qualifies_as_work_accident}"


class Recommendation(models.Model):
    """
    Recommendations for providing missing documents .
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    analysis = models.ForeignKey(Analysis, on_delete=models.CASCADE, related_name='recommendations')
    
    document_type = models.ForeignKey(DocumentType, on_delete=models.PROTECT)
    reason = models.TextField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Request for {self.document_type.name}"


class Opinion(models.Model):
    """
    Final opinion regarding applicability for work accident compensation.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    analysis = models.OneToOneField(Analysis, on_delete=models.CASCADE, related_name='opinion')
    
    summary = models.TextField()
    detailed_analysis = models.TextField()
    
    overall_assessment = models.CharField(max_length=100)
    
    generated_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Opinion: {self.overall_assessment}"


class DraftDocument(models.Model):
    """
    Generated output document files (Karta Wypadku).
    """
    FORMAT_CHOICES = [
        ('pdf', 'PDF'),
        ('docx', 'DOCX'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    analysis = models.ForeignKey(Analysis, on_delete=models.CASCADE, related_name='drafts')
    format = models.CharField(max_length=10, choices=FORMAT_CHOICES)

    file = models.FileField(upload_to='drafts/%Y/%m/%d/')
    generated_at = models.DateTimeField(auto_now_add=True)
    file_size = models.IntegerField()
    
    def __str__(self):
        return f"{self.format.upper()} draft"