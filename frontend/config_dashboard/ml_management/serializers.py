from rest_framework import serializers
from .models import MLModel, ModelMetrics, TrainingJob

class MLModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = MLModel
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

class ModelMetricsSerializer(serializers.ModelSerializer):
    model_name = serializers.CharField(source='model.name', read_only=True)
    model_version = serializers.CharField(source='model.version', read_only=True)
    
    class Meta:
        model = ModelMetrics
        fields = '__all__'
        read_only_fields = ('timestamp',)

class TrainingJobSerializer(serializers.ModelSerializer):
    model_name = serializers.CharField(source='model.name', read_only=True)
    
    class Meta:
        model = TrainingJob
        fields = '__all__'
        read_only_fields = ('start_time', 'end_time')
