from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from django.utils import timezone
from .models import Event, Signal, Correlation
from .serializers import EventSerializer, SignalSerializer, CorrelationSerializer
from .tasks import process_new_signal

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'type']
    ordering_fields = ['created_at', 'started_at', 'severity', 'confidence_score']
    
    @action(detail=False, methods=['get'])
    def nearby(self, request):
        """Get events near a specific location"""
        lat = float(request.query_params.get('lat', 0))
        lon = float(request.query_params.get('lon', 0))
        radius = float(request.query_params.get('radius', 10000))  # Default 10km
        
        point = Point(lon, lat, srid=4326)
        queryset = self.get_queryset().annotate(
            distance=Distance('location', point)
        ).filter(distance__lte=radius)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get all active events"""
        queryset = self.get_queryset().filter(status='active')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Mark an event as resolved"""
        event = self.get_object()
        event.status = 'resolved'
        event.ended_at = timezone.now()
        event.save()
        return Response({'status': 'event resolved'})

class SignalViewSet(viewsets.ModelViewSet):
    queryset = Signal.objects.all()
    serializer_class = SignalSerializer
    
    def create(self, request, *args, **kwargs):
        """Create a new signal and trigger processing"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        # Trigger async processing
        process_new_signal.delay(serializer.data)
        
        return Response(serializer.data, status=201)
    
    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """Get signals grouped by type"""
        signal_type = request.query_params.get('type')
        queryset = self.get_queryset()
        
        if signal_type:
            queryset = queryset.filter(type=signal_type)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class CorrelationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Correlation.objects.all()
    serializer_class = CorrelationSerializer
    
    @action(detail=False, methods=['get'])
    def by_signal(self, request):
        """Get correlations for a specific signal"""
        signal_id = request.query_params.get('signal_id')
        if signal_id:
            queryset = self.get_queryset().filter(
                source_signal_id=signal_id
            ) | self.get_queryset().filter(
                target_signal_id=signal_id
            )
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        return Response({'error': 'signal_id parameter is required'}, status=400)
