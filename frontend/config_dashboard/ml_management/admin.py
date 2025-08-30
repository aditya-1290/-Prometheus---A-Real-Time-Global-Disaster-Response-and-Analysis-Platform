from django.contrib import admin
from .models import MLModel, ModelMetrics, TrainingJob

@admin.register(MLModel)
class MLModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'version', 'model_type', 'status', 'updated_at')
    list_filter = ('model_type', 'status')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(ModelMetrics)
class ModelMetricsAdmin(admin.ModelAdmin):
    list_display = ('model', 'accuracy', 'precision', 'recall', 'f1_score', 'latency', 'timestamp')
    list_filter = ('model',)
    date_hierarchy = 'timestamp'

@admin.register(TrainingJob)
class TrainingJobAdmin(admin.ModelAdmin):
    list_display = ('model', 'status', 'start_time', 'end_time')
    list_filter = ('status', 'model')
    search_fields = ('error_message',)
    readonly_fields = ('start_time', 'end_time')
