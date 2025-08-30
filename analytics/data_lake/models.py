from django.db import models
from django.contrib.postgres.fields import JSONField

class DataSource(models.Model):
    """Data sources that feed into the data lake"""
    SOURCE_TYPES = [
        ('social_media', 'Social Media'),
        ('satellite', 'Satellite Imagery'),
        ('sensor', 'Sensor Network'),
        ('news', 'News Feed'),
        ('emergency', 'Emergency Services'),
    ]
    
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=20, choices=SOURCE_TYPES)
    endpoint = models.URLField()
    credentials = JSONField(default=dict)
    configuration = JSONField(default=dict)
    is_active = models.BooleanField(default=True)
    last_ingestion = models.DateTimeField(null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Dataset(models.Model):
    """Datasets stored in the data lake"""
    FORMAT_TYPES = [
        ('parquet', 'Parquet'),
        ('json', 'JSON'),
        ('csv', 'CSV'),
        ('image', 'Image'),
        ('video', 'Video'),
        ('audio', 'Audio'),
    ]
    
    source = models.ForeignKey(DataSource, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField()
    format = models.CharField(max_length=20, choices=FORMAT_TYPES)
    s3_path = models.CharField(max_length=255)
    size_bytes = models.BigIntegerField()
    row_count = models.BigIntegerField(null=True)
    schema = JSONField(null=True)
    metadata = JSONField(default=dict)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['format', 'created_at']),
        ]

class DatasetVersion(models.Model):
    """Versions of datasets for tracking changes"""
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    version = models.CharField(max_length=50)
    s3_path = models.CharField(max_length=255)
    changes = JSONField()
    is_current = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('dataset', 'version')

class ProcessingJob(models.Model):
    """Data processing jobs"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    source_dataset = models.ForeignKey(
        Dataset,
        related_name='processing_jobs',
        on_delete=models.CASCADE
    )
    job_type = models.CharField(max_length=50)
    parameters = JSONField(default=dict)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    error_message = models.TextField(null=True)
    result_location = models.CharField(max_length=255, null=True)
    
    started_at = models.DateTimeField(null=True)
    completed_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['status', 'job_type']),
            models.Index(fields=['created_at']),
        ]
