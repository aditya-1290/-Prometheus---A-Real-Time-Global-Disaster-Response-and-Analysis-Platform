from celery import shared_task
from django.utils import timezone
from datetime import timedelta
import requests
import hmac
import hashlib
import json
from .models import APIKey, APIUsageLog, WebhookConfig, APIEndpoint

@shared_task
def cleanup_expired_api_keys():
    """Deactivate expired API keys"""
    expired_keys = APIKey.objects.filter(
        expires_at__lt=timezone.now(),
        active=True
    )
    expired_keys.update(active=False)

@shared_task
def monitor_api_usage():
    """Monitor API usage for rate limiting and alerts"""
    endpoints = APIEndpoint.objects.all()
    
    for endpoint in endpoints:
        # Check last minute's usage
        minute_ago = timezone.now() - timedelta(minutes=1)
        requests_count = APIUsageLog.objects.filter(
            endpoint=endpoint,
            timestamp__gte=minute_ago
        ).count()
        
        if requests_count > endpoint.rate_limit:
            # Rate limit exceeded
            print(f"Rate limit exceeded for endpoint {endpoint.path}")
            
        # Check error rates
        total_requests = APIUsageLog.objects.filter(
            endpoint=endpoint,
            timestamp__gte=minute_ago
        ).count()
        
        error_requests = APIUsageLog.objects.filter(
            endpoint=endpoint,
            timestamp__gte=minute_ago,
            status_code__gte=400
        ).count()
        
        if total_requests > 0:
            error_rate = error_requests / total_requests
            if error_rate > 0.1:  # More than 10% errors
                print(f"High error rate for endpoint {endpoint.path}")

@shared_task
def process_webhook_queue():
    """Process queued webhook events"""
    active_webhooks = WebhookConfig.objects.filter(active=True)
    
    for webhook in active_webhooks:
        try:
            # Prepare the payload
            payload = {
                'event_type': webhook.event_type,
                'timestamp': timezone.now().isoformat(),
                'data': {}  # Add relevant data based on event type
            }
            
            # Calculate signature
            signature = hmac.new(
                webhook.secret_key.encode(),
                json.dumps(payload).encode(),
                hashlib.sha256
            ).hexdigest()
            
            # Send webhook
            headers = {
                'Content-Type': 'application/json',
                'X-Webhook-Signature': signature
            }
            
            response = requests.post(
                webhook.url,
                json=payload,
                headers=headers,
                timeout=5
            )
            
            if response.status_code != 200:
                raise Exception(f"Webhook failed with status {response.status_code}")
                
            webhook.last_triggered = timezone.now()
            webhook.save()
            
        except Exception as e:
            print(f"Error processing webhook {webhook.name}: {e}")

@shared_task
def cleanup_api_logs():
    """Clean up old API usage logs"""
    # Keep only last 30 days of logs
    threshold = timezone.now() - timedelta(days=30)
    APIUsageLog.objects.filter(timestamp__lt=threshold).delete()
