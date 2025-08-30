from rest_framework import serializers
from .models import APIKey, APIEndpoint, APIUsageLog, WebhookConfig

class APIKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = APIKey
        fields = '__all__'
        read_only_fields = ('key', 'created_at', 'last_used')
        extra_kwargs = {
            'key': {'write_only': True}
        }

class APIEndpointSerializer(serializers.ModelSerializer):
    class Meta:
        model = APIEndpoint
        fields = '__all__'
        read_only_fields = ('created_at',)

class APIUsageLogSerializer(serializers.ModelSerializer):
    endpoint_path = serializers.CharField(source='endpoint.path', read_only=True)
    api_key_name = serializers.CharField(source='api_key.name', read_only=True)
    
    class Meta:
        model = APIUsageLog
        fields = '__all__'
        read_only_fields = ('timestamp',)

class WebhookConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebhookConfig
        fields = '__all__'
        read_only_fields = ('created_at', 'last_triggered')
        extra_kwargs = {
            'secret_key': {'write_only': True}
        }
