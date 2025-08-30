from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.contrib.gis.db.models.functions import Distance
from .models import Region, RiskZone, Asset, ImpactZone
from .serializers import RegionSerializer, RiskZoneSerializer, AssetSerializer, ImpactZoneSerializer
from .tasks import calculate_impact_zone, assess_infrastructure_impact, update_asset_status

class RegionViewSet(viewsets.ModelViewSet):
    queryset = Region.objects.all()
    serializer_class = RegionSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'code', 'type']
    
    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """Get regions filtered by type"""
        region_type = request.query_params.get('type')
        if region_type:
            queryset = self.get_queryset().filter(type=region_type)
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        return Response({'error': 'type parameter is required'}, status=400)

class RiskZoneViewSet(viewsets.ModelViewSet):
    queryset = RiskZone.objects.all()
    serializer_class = RiskZoneSerializer
    
    @action(detail=False, methods=['get'])
    def active_risks(self, request):
        """Get currently active risk zones"""
        risk_type = request.query_params.get('type')
        risk_level = request.query_params.get('level')
        
        queryset = self.get_queryset()
        if risk_type:
            queryset = queryset.filter(risk_type=risk_type)
        if risk_level:
            queryset = queryset.filter(risk_level=risk_level)
            
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class AssetViewSet(viewsets.ModelViewSet):
    queryset = Asset.objects.all()
    serializer_class = AssetSerializer
    
    @action(detail=False, methods=['get'])
    def nearby(self, request):
        """Find nearby assets"""
        try:
            lat = float(request.query_params.get('lat', 0))
            lon = float(request.query_params.get('lon', 0))
            radius = float(request.query_params.get('radius', 5000))  # Default 5km
            asset_type = request.query_params.get('type')
            
            point = Point(lon, lat, srid=4326)
            queryset = self.get_queryset()
            
            if asset_type:
                queryset = queryset.filter(asset_type=asset_type)
            
            queryset = queryset.filter(
                location__distance_lte=(point, D(m=radius))
            ).annotate(
                distance=Distance('location', point)
            ).order_by('distance')
            
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
            
        except ValueError:
            return Response({'error': 'Invalid coordinates'}, status=400)
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Update asset operational status"""
        status = request.data.get('status')
        if status not in ['operational', 'limited', 'non-operational']:
            return Response({'error': 'Invalid status'}, status=400)
        
        asset = self.get_object()
        update_asset_status.delay(asset.id, status)
        
        return Response({'message': 'Status update initiated'})

class ImpactZoneViewSet(viewsets.ModelViewSet):
    queryset = ImpactZone.objects.all()
    serializer_class = ImpactZoneSerializer
    
    @action(detail=False, methods=['get'])
    def current_impacts(self, request):
        """Get current impact zones"""
        severity = request.query_params.get('severity')
        
        queryset = self.get_queryset()
        if severity:
            queryset = queryset.filter(severity=severity)
            
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def recalculate(self, request, pk=None):
        """Recalculate impact zone"""
        impact_zone = self.get_object()
        calculate_impact_zone.delay(impact_zone.event.id)
        assess_infrastructure_impact.delay(impact_zone.id)
        
        return Response({'message': 'Impact zone recalculation initiated'})
