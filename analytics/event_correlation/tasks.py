from celery import shared_task
import numpy as np
from sklearn.cluster import DBSCAN
from django.contrib.gis.geos import Point
from django.utils import timezone
from datetime import timedelta
from .models import Event, Signal, Correlation

@shared_task
def process_new_signal(signal_data):
    """Process a new signal and look for correlations"""
    # Create new signal
    signal = Signal.objects.create(**signal_data)
    
    # Look for related signals in space and time
    time_window = signal.timestamp - timedelta(hours=24)
    nearby_signals = Signal.objects.filter(
        location__distance_lte=(signal.location, 5000),  # Within 5km
        timestamp__gte=time_window,
        type__in=[s[0] for s in Signal.SIGNAL_TYPES if s[0] != signal.type]
    )
    
    # If we find related signals, analyze correlations
    if nearby_signals.exists():
        analyze_correlations.delay(signal.id, [s.id for s in nearby_signals])

@shared_task
def analyze_correlations(source_signal_id, target_signal_ids):
    """Analyze correlations between signals"""
    source_signal = Signal.objects.get(id=source_signal_id)
    target_signals = Signal.objects.filter(id__in=target_signal_ids)
    
    for target in target_signals:
        # Calculate spatial correlation
        distance = source_signal.location.distance(target.location)
        spatial_correlation = 1 / (1 + distance/1000)  # Normalize by km
        
        # Calculate temporal correlation
        time_diff = abs((source_signal.timestamp - target.timestamp).total_seconds())
        temporal_correlation = 1 / (1 + time_diff/3600)  # Normalize by hour
        
        # Combined correlation strength
        strength = (spatial_correlation + temporal_correlation) / 2
        
        if strength > 0.5:  # If correlation is significant
            Correlation.objects.create(
                source_signal=source_signal,
                target_signal=target,
                correlation_type='spatiotemporal',
                strength=strength
            )
            
            # Check if we should create or update an event
            check_event_creation.delay(source_signal_id, target.id)

@shared_task
def check_event_creation(signal_id, correlated_signal_id):
    """Check if we should create a new event or update an existing one"""
    signal = Signal.objects.get(id=signal_id)
    correlated_signal = Signal.objects.get(id=correlated_signal_id)
    
    # Get all related correlations
    correlations = Correlation.objects.filter(
        source_signal__in=[signal, correlated_signal]
    ).select_related('source_signal', 'target_signal')
    
    if correlations.count() >= 3:  # If we have enough correlated signals
        # Extract signal locations for clustering
        locations = []
        for corr in correlations:
            locations.extend([
                [corr.source_signal.location.x, corr.source_signal.location.y],
                [corr.target_signal.location.x, corr.target_signal.location.y]
            ])
        
        # Cluster locations
        clustering = DBSCAN(eps=0.1, min_samples=3).fit(np.array(locations))
        
        if len(set(clustering.labels_)) > 1:  # If we found clusters
            for label in set(clustering.labels_):
                if label == -1:  # Skip noise
                    continue
                
                # Calculate cluster center
                cluster_points = np.array(locations)[clustering.labels_ == label]
                center = cluster_points.mean(axis=0)
                
                # Create or update event
                event, created = Event.objects.get_or_create(
                    location=Point(center[0], center[1]),
                    status='active',
                    defaults={
                        'type': 'natural',  # Default type
                        'title': f'Detected Event at {center}',
                        'description': 'Automatically detected event from correlated signals',
                        'severity': 'medium',
                        'radius_meters': 5000,  # Default 5km radius
                        'started_at': timezone.now(),
                    }
                )
                
                # Update confidence score based on number of signals
                event.confidence_score = min(0.95, 0.5 + (correlations.count() * 0.1))
                event.save()
                
                # Associate signals with event
                Signal.objects.filter(
                    id__in=[signal_id, correlated_signal_id]
                ).update(event=event)
