from rest_framework import serializers
from .models import (
    DisasterConfig,
    ResourceType,
    AlertConfig,
    SystemConfig
)

class DisasterConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = DisasterConfig
        fields = '__all__'

class ResourceTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResourceType
        fields = '__all__'

class AlertConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlertConfig
        fields = '__all__'

class SystemConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemConfig
        fields = '__all__'
