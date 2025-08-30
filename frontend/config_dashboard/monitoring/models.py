from django.db import models

class ServiceHealth(models.Model):
    SERVICE_TYPES = (
        ('data_ingestion', 'Data Ingestion'),
        ('ml_processing', 'ML Processing'),
        ('analytics', 'Analytics'),
        ('api', 'API Services'),
    )

    STATUS_CHOICES = (
        ('healthy', 'Healthy'),
        ('degraded', 'Degraded'),
        ('down', 'Down'),
    )

    name = models.CharField(max_length=100)
    service_type = models.CharField(max_length=20, choices=SERVICE_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    last_check = models.DateTimeField(auto_now=True)
    response_time = models.FloatField(null=True)
    error_count = models.IntegerField(default=0)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['service_type', 'name']

class PerformanceMetric(models.Model):
    METRIC_TYPES = (
        ('cpu_usage', 'CPU Usage'),
        ('memory_usage', 'Memory Usage'),
        ('disk_usage', 'Disk Usage'),
        ('network_latency', 'Network Latency'),
        ('request_rate', 'Request Rate'),
        ('error_rate', 'Error Rate'),
    )

    service = models.ForeignKey(ServiceHealth, on_delete=models.CASCADE)
    metric_type = models.CharField(max_length=20, choices=METRIC_TYPES)
    value = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)
    threshold = models.FloatField(null=True)

    class Meta:
        ordering = ['-timestamp']

class AlertLog(models.Model):
    SEVERITY_LEVELS = (
        ('info', 'Information'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('critical', 'Critical'),
    )

    service = models.ForeignKey(ServiceHealth, on_delete=models.CASCADE)
    severity = models.CharField(max_length=20, choices=SEVERITY_LEVELS)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(null=True)
    resolution_notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-timestamp']
