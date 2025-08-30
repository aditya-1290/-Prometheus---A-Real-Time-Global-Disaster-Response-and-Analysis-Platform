from django.db import models

class MLModel(models.Model):
    MODEL_TYPES = (
        ('nlp', 'Natural Language Processing'),
        ('cv', 'Computer Vision'),
        ('audio', 'Audio Processing'),
        ('multimodal', 'Multimodal'),
    )

    STATUS_CHOICES = (
        ('development', 'In Development'),
        ('training', 'Training'),
        ('deployed', 'Deployed'),
        ('deprecated', 'Deprecated'),
    )

    name = models.CharField(max_length=100)
    version = models.CharField(max_length=20)
    model_type = models.CharField(max_length=20, choices=MODEL_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    description = models.TextField()
    artifacts_path = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
        unique_together = ['name', 'version']

class ModelMetrics(models.Model):
    model = models.ForeignKey(MLModel, on_delete=models.CASCADE)
    accuracy = models.FloatField()
    precision = models.FloatField()
    recall = models.FloatField()
    f1_score = models.FloatField()
    latency = models.FloatField()  # inference time in ms
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']

class TrainingJob(models.Model):
    STATUS_CHOICES = (
        ('queued', 'Queued'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )

    model = models.ForeignKey(MLModel, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    hyperparameters = models.JSONField()
    training_data_path = models.CharField(max_length=255)
    validation_data_path = models.CharField(max_length=255)
    start_time = models.DateTimeField(null=True)
    end_time = models.DateTimeField(null=True)
    logs_path = models.CharField(max_length=255, null=True)
    error_message = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-start_time']
