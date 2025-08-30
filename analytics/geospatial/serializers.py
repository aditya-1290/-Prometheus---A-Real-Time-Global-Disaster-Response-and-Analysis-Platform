from rest_framework import serializers
from .models import Region, RiskZone, Asset, ImpactZone

class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = '__all__'

class RiskZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = RiskZone
        fields = '__all__'

class AssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asset
        fields = '__all__'

class ImpactZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImpactZone
        fields = '__all__'
