from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import DataSource, Dataset, DatasetVersion, ProcessingJob
from .serializers import (
    DataSourceSerializer, DatasetSerializer,
    DatasetVersionSerializer, ProcessingJobSerializer
)
from .tasks import ingest_data, process_dataset

class DataSourceViewSet(viewsets.ModelViewSet):
    queryset = DataSource.objects.all()
    serializer_class = DataSourceSerializer
    
    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """Toggle the active status of a data source"""
        source = self.get_object()
        source.is_active = not source.is_active
        source.save()
        return Response({'status': 'active' if source.is_active else 'inactive'})
    
    @action(detail=True, methods=['post'])
    def ingest(self, request, pk=None):
        """Trigger data ingestion from a source"""
        source = self.get_object()
        data = request.data.get('data')
        format_type = request.data.get('format', 'json')
        
        if not data:
            return Response(
                {'error': 'No data provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        task = ingest_data.delay(source.id, data, format_type)
        return Response({
            'status': 'ingestion started',
            'task_id': task.id
        })

class DatasetViewSet(viewsets.ModelViewSet):
    queryset = Dataset.objects.all()
    serializer_class = DatasetSerializer
    
    @action(detail=True, methods=['post'])
    def process(self, request, pk=None):
        """Create a processing job for the dataset"""
        dataset = self.get_object()
        job_type = request.data.get('job_type')
        parameters = request.data.get('parameters', {})
        
        if not job_type:
            return Response(
                {'error': 'job_type is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        job = ProcessingJob.objects.create(
            source_dataset=dataset,
            job_type=job_type,
            parameters=parameters,
            status='pending'
        )
        
        task = process_dataset.delay(job.id)
        
        return Response({
            'status': 'processing started',
            'job_id': job.id,
            'task_id': task.id
        })
    
    @action(detail=True, methods=['post'])
    def version(self, request, pk=None):
        """Create a new version of the dataset"""
        dataset = self.get_object()
        version = request.data.get('version')
        changes = request.data.get('changes', {})
        
        if not version:
            return Response(
                {'error': 'version is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Set previous versions as not current
        DatasetVersion.objects.filter(dataset=dataset).update(is_current=False)
        
        # Create new version
        DatasetVersion.objects.create(
            dataset=dataset,
            version=version,
            s3_path=dataset.s3_path,
            changes=changes,
            is_current=True
        )
        
        return Response({'status': 'version created'})

class DatasetVersionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DatasetVersion.objects.all()
    serializer_class = DatasetVersionSerializer
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """Get all current versions"""
        queryset = self.get_queryset().filter(is_current=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class ProcessingJobViewSet(viewsets.ModelViewSet):
    queryset = ProcessingJob.objects.all()
    serializer_class = ProcessingJobSerializer
    
    @action(detail=True, methods=['post'])
    def retry(self, request, pk=None):
        """Retry a failed job"""
        job = self.get_object()
        
        if job.status != 'failed':
            return Response(
                {'error': 'Only failed jobs can be retried'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        job.status = 'pending'
        job.error_message = None
        job.started_at = None
        job.completed_at = None
        job.save()
        
        task = process_dataset.delay(job.id)
        
        return Response({
            'status': 'job restarted',
            'task_id': task.id
        })
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a pending or running job"""
        job = self.get_object()
        
        if job.status not in ['pending', 'running']:
            return Response(
                {'error': 'Only pending or running jobs can be cancelled'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        job.status = 'failed'
        job.error_message = 'Cancelled by user'
        job.completed_at = timezone.now()
        job.save()
        
        return Response({'status': 'job cancelled'})
