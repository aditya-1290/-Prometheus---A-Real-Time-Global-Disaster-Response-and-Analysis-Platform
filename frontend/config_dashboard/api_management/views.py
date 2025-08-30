from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
import secrets
from .models import APIKey, APIEndpoint, APIUsageLog, WebhookConfig
from .serializers import (
    APIKeySerializer, APIEndpointSerializer,
    APIUsageLogSerializer, WebhookConfigSerializer
)

class APIKeyViewSet(viewsets.ModelViewSet):
    queryset = APIKey.objects.all()
    serializer_class = APIKeySerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['key_type', 'active']
    ordering_fields = ['created_at', 'name']

    def perform_create(self, serializer):
        """Generate a new API key when creating"""
        api_key = secrets.token_hex(32)
        serializer.save(key=api_key)

    @action(detail=True, methods=['post'])
    def regenerate(self, request, pk=None):
        """Regenerate API key"""
        api_key = self.get_object()
        new_key = secrets.token_hex(32)
        api_key.key = new_key
        api_key.save()
        return Response({'key': new_key})

    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate API key"""
        api_key = self.get_object()
        api_key.active = False
        api_key.save()
        return Response({'status': 'key deactivated'})

class APIEndpointViewSet(viewsets.ModelViewSet):
    queryset = APIEndpoint.objects.all()
    serializer_class = APIEndpointSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['method', 'requires_auth', 'deprecated']
    ordering_fields = ['path', 'method']

    @action(detail=False, methods=['get'])
    def usage_stats(self, request):
        """Get usage statistics for endpoints"""
        endpoint_id = request.query_params.get('endpoint_id')
        time_range = request.query_params.get('time_range', '24h')
        
        logs = APIUsageLog.objects.filter(endpoint_id=endpoint_id)
        
        stats = {
            'total_requests': logs.count(),
            'average_response_time': logs.aggregate(avg_time=models.Avg('response_time'))['avg_time'],
            'error_rate': (
                logs.filter(status_code__gte=400).count() / logs.count() * 100
                if logs.count() > 0 else 0
            )
        }
        return Response(stats)

class APIUsageLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = APIUsageLog.objects.all()
    serializer_class = APIUsageLogSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['endpoint', 'api_key', 'status_code']
    ordering_fields = ['timestamp', 'response_time']

    @action(detail=False, methods=['get'])
    def error_summary(self, request):
        """Get summary of API errors"""
        logs = self.queryset.filter(status_code__gte=400)
        summary = logs.values('status_code').annotate(
            count=models.Count('id'),
            avg_response_time=models.Avg('response_time')
        )
        return Response(summary)

class WebhookConfigViewSet(viewsets.ModelViewSet):
    queryset = WebhookConfig.objects.all()
    serializer_class = WebhookConfigSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['event_type', 'active']
    ordering_fields = ['name', 'last_triggered']

    def perform_create(self, serializer):
        """Generate a secret key when creating webhook"""
        secret_key = secrets.token_hex(32)
        serializer.save(secret_key=secret_key)

    @action(detail=True, methods=['post'])
    def test_webhook(self, request, pk=None):
        """Test webhook by sending a test event"""
        webhook = self.get_object()
        try:
            # Send test event
            success = send_test_webhook(webhook)
            if success:
                return Response({'status': 'test successful'})
            return Response(
                {'error': 'webhook test failed'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
