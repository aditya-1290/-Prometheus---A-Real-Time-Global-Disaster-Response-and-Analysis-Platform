from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from .models import MLModel, ModelMetrics, TrainingJob
from .serializers import MLModelSerializer, ModelMetricsSerializer, TrainingJobSerializer

class MLModelViewSet(viewsets.ModelViewSet):
    queryset = MLModel.objects.all()
    serializer_class = MLModelSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['model_type', 'status']
    ordering_fields = ['name', 'version', 'updated_at']

    @action(detail=True, methods=['post'])
    def deploy(self, request, pk=None):
        """Deploy a model to production"""
        model = self.get_object()
        model.status = 'deployed'
        model.save()
        return Response({'status': 'model deployed'})

    @action(detail=True, methods=['post'])
    def deprecate(self, request, pk=None):
        """Deprecate a model"""
        model = self.get_object()
        model.status = 'deprecated'
        model.save()
        return Response({'status': 'model deprecated'})

class ModelMetricsViewSet(viewsets.ModelViewSet):
    queryset = ModelMetrics.objects.all()
    serializer_class = ModelMetricsSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['model']
    ordering_fields = ['timestamp']

    @action(detail=False, methods=['get'])
    def performance_trend(self, request):
        """Get performance trend for a specific model"""
        model_id = request.query_params.get('model_id')
        metrics = self.queryset.filter(model_id=model_id).order_by('timestamp')
        
        trend_data = {
            'timestamps': [],
            'accuracy': [],
            'latency': []
        }
        
        for metric in metrics:
            trend_data['timestamps'].append(metric.timestamp)
            trend_data['accuracy'].append(metric.accuracy)
            trend_data['latency'].append(metric.latency)
            
        return Response(trend_data)

class TrainingJobViewSet(viewsets.ModelViewSet):
    queryset = TrainingJob.objects.all()
    serializer_class = TrainingJobSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['model', 'status']
    ordering_fields = ['start_time']

    @action(detail=True, methods=['post'])
    def start_training(self, request, pk=None):
        """Start a training job"""
        job = self.get_object()
        if job.status != 'queued':
            return Response(
                {'error': 'Job must be in queued state to start'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        job.status = 'running'
        job.start_time = timezone.now()
        job.save()
        
        # Trigger async training task
        train_model.delay(job.id)
        return Response({'status': 'training started'})

    @action(detail=True, methods=['post'])
    def cancel_training(self, request, pk=None):
        """Cancel a training job"""
        job = self.get_object()
        if job.status not in ['queued', 'running']:
            return Response(
                {'error': 'Can only cancel queued or running jobs'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        job.status = 'failed'
        job.end_time = timezone.now()
        job.error_message = 'Training cancelled by user'
        job.save()
        return Response({'status': 'training cancelled'})
