from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import ServiceHealth, PerformanceMetric, AlertLog
from .serializers import ServiceHealthSerializer, PerformanceMetricSerializer, AlertLogSerializer

class ServiceHealthViewSet(viewsets.ModelViewSet):
    queryset = ServiceHealth.objects.all()
    serializer_class = ServiceHealthSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['service_type', 'status']
    ordering_fields = ['name', 'last_check', 'status']

    @action(detail=False, methods=['get'])
    def system_status(self, request):
        """Get overall system health status"""
        total_services = ServiceHealth.objects.count()
        healthy_services = ServiceHealth.objects.filter(status='healthy').count()
        status_summary = {
            'total_services': total_services,
            'healthy_services': healthy_services,
            'degraded_services': ServiceHealth.objects.filter(status='degraded').count(),
            'down_services': ServiceHealth.objects.filter(status='down').count(),
            'health_percentage': (healthy_services / total_services * 100) if total_services > 0 else 0
        }
        return Response(status_summary)

class PerformanceMetricViewSet(viewsets.ModelViewSet):
    queryset = PerformanceMetric.objects.all()
    serializer_class = PerformanceMetricSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['service', 'metric_type']
    ordering_fields = ['timestamp', 'value']

    @action(detail=False, methods=['get'])
    def service_metrics(self, request):
        """Get aggregated metrics for all services"""
        service_id = request.query_params.get('service_id')
        time_range = request.query_params.get('time_range', '24h')  # Default to last 24 hours
        
        metrics = PerformanceMetric.objects.filter(
            service_id=service_id
        ).order_by('timestamp')
        
        aggregated_data = {
            'cpu_usage': self._aggregate_metric(metrics, 'cpu_usage'),
            'memory_usage': self._aggregate_metric(metrics, 'memory_usage'),
            'response_time': self._aggregate_metric(metrics, 'response_time')
        }
        return Response(aggregated_data)

    def _aggregate_metric(self, metrics, metric_type):
        metric_data = metrics.filter(metric_type=metric_type)
        if not metric_data:
            return None
        return {
            'current': metric_data.last().value if metric_data.exists() else None,
            'average': metric_data.aggregate(avg_value=models.Avg('value'))['avg_value'],
            'max': metric_data.aggregate(max_value=models.Max('value'))['max_value']
        }

class AlertLogViewSet(viewsets.ModelViewSet):
    queryset = AlertLog.objects.all()
    serializer_class = AlertLogSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['service', 'severity', 'resolved']
    ordering_fields = ['timestamp', 'severity']

    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Mark an alert as resolved"""
        alert = self.get_object()
        alert.resolved = True
        alert.resolved_at = timezone.now()
        alert.resolution_notes = request.data.get('resolution_notes', '')
        alert.save()
        return Response({'status': 'alert resolved'})
