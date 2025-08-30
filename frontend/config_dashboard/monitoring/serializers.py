from rest_framework import serializers
from .models import ServiceHealth, PerformanceMetric, AlertLog

class ServiceHealthSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceHealth
        fields = '__all__'
        read_only_fields = ('last_check', 'error_count')

class PerformanceMetricSerializer(serializers.ModelSerializer):
    service_name = serializers.CharField(source='service.name', read_only=True)
    
    class Meta:
        model = PerformanceMetric
        fields = '__all__'
        read_only_fields = ('timestamp',)

class AlertLogSerializer(serializers.ModelSerializer):
    service_name = serializers.CharField(source='service.name', read_only=True)
    
    class Meta:
        model = AlertLog
        fields = '__all__'
        read_only_fields = ('timestamp',)
