from django.db import models

class APIKey(models.Model):
    KEY_TYPES = (
        ('internal', 'Internal Service'),
        ('external', 'External Client'),
        ('partner', 'Partner Organization'),
    )

    name = models.CharField(max_length=100)
    key_type = models.CharField(max_length=20, choices=KEY_TYPES)
    key = models.CharField(max_length=64, unique=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True)
    last_used = models.DateTimeField(null=True)
    
    class Meta:
        ordering = ['-created_at']

class APIEndpoint(models.Model):
    METHOD_CHOICES = (
        ('GET', 'GET'),
        ('POST', 'POST'),
        ('PUT', 'PUT'),
        ('DELETE', 'DELETE'),
    )

    path = models.CharField(max_length=255)
    method = models.CharField(max_length=10, choices=METHOD_CHOICES)
    description = models.TextField()
    rate_limit = models.IntegerField(default=100)  # requests per minute
    requires_auth = models.BooleanField(default=True)
    deprecated = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['path', 'method']
        ordering = ['path', 'method']

class APIUsageLog(models.Model):
    endpoint = models.ForeignKey(APIEndpoint, on_delete=models.CASCADE)
    api_key = models.ForeignKey(APIKey, null=True, on_delete=models.SET_NULL)
    timestamp = models.DateTimeField(auto_now_add=True)
    response_time = models.FloatField()  # in milliseconds
    status_code = models.IntegerField()
    error_message = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField()
    
    class Meta:
        ordering = ['-timestamp']

class WebhookConfig(models.Model):
    EVENT_TYPES = (
        ('disaster_detected', 'Disaster Detected'),
        ('alert_triggered', 'Alert Triggered'),
        ('resource_deployed', 'Resource Deployed'),
        ('status_updated', 'Status Updated'),
    )

    name = models.CharField(max_length=100)
    url = models.URLField()
    event_type = models.CharField(max_length=30, choices=EVENT_TYPES)
    active = models.BooleanField(default=True)
    secret_key = models.CharField(max_length=64)
    retry_count = models.IntegerField(default=3)
    created_at = models.DateTimeField(auto_now_add=True)
    last_triggered = models.DateTimeField(null=True)
    
    class Meta:
        ordering = ['name']
