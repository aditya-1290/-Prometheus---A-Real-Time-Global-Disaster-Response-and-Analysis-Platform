from django.db import models
from django.contrib.gis.db import models as gis_models
from django.contrib.postgres.fields import JSONField

class Event(models.Model):
    """Base model for all events in the system"""
    EVENT_TYPES = [
        ('natural', 'Natural Disaster'),
        ('man_made', 'Man-made Disaster'),
        ('health', 'Health Crisis'),
        ('other', 'Other'),
    ]
    
    SEVERITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending Verification'),
        ('active', 'Active'),
        ('resolved', 'Resolved'),
        ('false_alarm', 'False Alarm'),
    ]
    
    type = models.CharField(max_length=20, choices=EVENT_TYPES)
    title = models.CharField(max_length=255)
    description = models.TextField()
    severity = models.CharField(max_length=10, choices=SEVERITY_LEVELS)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    location = gis_models.PointField()
    radius_meters = models.FloatField(help_text='Affected area radius in meters')
    
    started_at = models.DateTimeField()
    ended_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    metadata = JSONField(default=dict)
    confidence_score = models.FloatField(
        default=0.0,
        help_text='Confidence score based on correlated signals'
    )
    
    class Meta:
        indexes = [
            models.Index(fields=['type', 'status', 'severity']),
            models.Index(fields=['started_at', 'ended_at']),
        ]

class Signal(models.Model):
    """Individual signals that contribute to event detection"""
    SIGNAL_TYPES = [
        ('social_media', 'Social Media'),
        ('satellite', 'Satellite Image'),
        ('sensor', 'Sensor Data'),
        ('news', 'News Report'),
        ('emergency_call', 'Emergency Call'),
    ]
    
    event = models.ForeignKey(Event, related_name='signals', on_delete=models.CASCADE)
    type = models.CharField(max_length=20, choices=SIGNAL_TYPES)
    source_id = models.CharField(max_length=255)
    timestamp = models.DateTimeField()
    location = gis_models.PointField()
    
    raw_data = JSONField()
    processed_data = JSONField()
    confidence_score = models.FloatField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['type', 'timestamp']),
            models.Index(fields=['event', 'type']),
        ]

class Correlation(models.Model):
    """Tracks correlations between signals"""
    source_signal = models.ForeignKey(
        Signal,
        related_name='source_correlations',
        on_delete=models.CASCADE
    )
    target_signal = models.ForeignKey(
        Signal,
        related_name='target_correlations',
        on_delete=models.CASCADE
    )
    correlation_type = models.CharField(max_length=50)
    strength = models.FloatField()
    metadata = JSONField(default=dict)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('source_signal', 'target_signal', 'correlation_type')
