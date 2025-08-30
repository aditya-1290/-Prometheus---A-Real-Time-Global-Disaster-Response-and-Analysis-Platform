from celery import shared_task
from django.utils import timezone
from datetime import timedelta
import requests
from .models import ServiceHealth, PerformanceMetric, AlertLog

@shared_task
def check_service_health():
    """Check health of all registered services"""
    services = ServiceHealth.objects.all()
    for service in services:
        try:
            # Try to contact service health endpoint
            response = requests.get(f"{service.url}/health", timeout=5)
            
            if response.status_code == 200:
                service.status = 'healthy'
                service.error_count = 0
            else:
                service.status = 'degraded'
                service.error_count += 1
                
            # Create performance metric
            PerformanceMetric.objects.create(
                service=service,
                metric_type='response_time',
                value=response.elapsed.total_seconds() * 1000  # Convert to ms
            )
            
        except requests.RequestException:
            service.status = 'down'
            service.error_count += 1
            
            # Create alert for down service
            if service.error_count >= 3:  # Alert after 3 consecutive failures
                AlertLog.objects.create(
                    service=service,
                    severity='critical',
                    message=f"Service {service.name} is down"
                )
        
        service.last_check = timezone.now()
        service.save()

@shared_task
def collect_performance_metrics():
    """Collect performance metrics from all services"""
    services = ServiceHealth.objects.all()
    for service in services:
        try:
            # Collect various metrics
            response = requests.get(f"{service.url}/metrics", timeout=5)
            metrics = response.json()
            
            # Store CPU usage
            PerformanceMetric.objects.create(
                service=service,
                metric_type='cpu_usage',
                value=metrics.get('cpu_usage', 0)
            )
            
            # Store memory usage
            PerformanceMetric.objects.create(
                service=service,
                metric_type='memory_usage',
                value=metrics.get('memory_usage', 0)
            )
            
            # Check for threshold violations
            if metrics.get('cpu_usage', 0) > 90:  # CPU usage above 90%
                AlertLog.objects.create(
                    service=service,
                    severity='warning',
                    message=f"High CPU usage detected for {service.name}"
                )
                
        except requests.RequestException:
            pass  # Health check task will handle service availability issues

@shared_task
def cleanup_old_metrics():
    """Clean up old performance metrics"""
    # Keep only last 30 days of metrics
    threshold = timezone.now() - timedelta(days=30)
    PerformanceMetric.objects.filter(timestamp__lt=threshold).delete()
    
    # Archive resolved alerts older than 90 days
    alert_threshold = timezone.now() - timedelta(days=90)
    AlertLog.objects.filter(
        resolved=True,
        timestamp__lt=alert_threshold
    ).delete()
