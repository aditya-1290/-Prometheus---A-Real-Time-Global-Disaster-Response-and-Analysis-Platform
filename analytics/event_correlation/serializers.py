from rest_framework import serializers
from .models import Event, Signal, Correlation

class SignalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Signal
        fields = '__all__'

class CorrelationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Correlation
        fields = '__all__'

class EventSerializer(serializers.ModelSerializer):
    signals = SignalSerializer(many=True, read_only=True)
    
    class Meta:
        model = Event
        fields = '__all__'
