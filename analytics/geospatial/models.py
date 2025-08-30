from django.contrib.gis.db import models
from django.contrib.postgres.fields import JSONField

class Region(models.Model):
    """Geographic regions for analysis"""
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50, unique=True)
    geometry = models.MultiPolygonField()
    type = models.CharField(max_length=50)  # e.g., city, state, country
    population = models.IntegerField(null=True)
    metadata = JSONField(default=dict)
    
    class Meta:
        indexes = [
            models.Index(fields=['type', 'name']),
        ]

class RiskZone(models.Model):
    """Areas identified as high-risk for specific disaster types"""
    RISK_TYPES = [
        ('flood', 'Flood Risk'),
        ('fire', 'Fire Risk'),
        ('earthquake', 'Earthquake Risk'),
        ('storm', 'Storm Risk'),
    ]
    
    RISK_LEVELS = [
        ('low', 'Low Risk'),
        ('medium', 'Medium Risk'),
        ('high', 'High Risk'),
        ('extreme', 'Extreme Risk'),
    ]
    
    region = models.ForeignKey(Region, related_name='risk_zones', on_delete=models.CASCADE)
    risk_type = models.CharField(max_length=20, choices=RISK_TYPES)
    risk_level = models.CharField(max_length=10, choices=RISK_LEVELS)
    geometry = models.PolygonField()
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField(null=True)
    confidence = models.FloatField()
    metadata = JSONField(default=dict)
    
    class Meta:
        indexes = [
            models.Index(fields=['risk_type', 'risk_level']),
            models.Index(fields=['valid_from', 'valid_until']),
        ]

class Asset(models.Model):
    """Critical infrastructure and assets"""
    ASSET_TYPES = [
        ('hospital', 'Hospital'),
        ('fire_station', 'Fire Station'),
        ('police', 'Police Station'),
        ('shelter', 'Emergency Shelter'),
        ('power_plant', 'Power Plant'),
        ('water_facility', 'Water Facility'),
    ]
    
    name = models.CharField(max_length=255)
    asset_type = models.CharField(max_length=20, choices=ASSET_TYPES)
    location = models.PointField()
    capacity = models.IntegerField(null=True)
    status = models.CharField(max_length=20, default='operational')
    region = models.ForeignKey(Region, related_name='assets', on_delete=models.SET_NULL, null=True)
    metadata = JSONField(default=dict)
    
    class Meta:
        indexes = [
            models.Index(fields=['asset_type', 'status']),
        ]

class ImpactZone(models.Model):
    """Areas currently affected by active disasters"""
    event = models.ForeignKey(
        'event_correlation.Event',
        related_name='impact_zones',
        on_delete=models.CASCADE
    )
    geometry = models.MultiPolygonField()
    severity = models.CharField(max_length=20)
    population_affected = models.IntegerField(default=0)
    assets_affected = models.ManyToManyField(Asset, related_name='impacts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    metadata = JSONField(default=dict)
    
    class Meta:
        indexes = [
            models.Index(fields=['severity', 'created_at']),
        ]
