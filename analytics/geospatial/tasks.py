from celery import shared_task
from django.contrib.gis.geos import MultiPolygon, Polygon
from django.contrib.gis.db.models.functions import Intersection, Area, Distance
from django.db.models import Sum
from .models import Region, RiskZone, Asset, ImpactZone
from event_correlation.models import Event

@shared_task
def update_risk_zones():
    """Update risk zones based on historical data and current conditions"""
    # This would typically involve:
    # 1. Analyzing historical event data
    # 2. Processing environmental data
    # 3. Applying risk models
    # For now, this is a placeholder
    pass

@shared_task
def calculate_impact_zone(event_id):
    """Calculate the impact zone for an event"""
    try:
        event = Event.objects.get(id=event_id)
        
        # Create a buffer around the event location
        impact_radius = event.radius_meters
        impact_area = event.location.buffer(impact_radius)
        
        if isinstance(impact_area, Polygon):
            impact_area = MultiPolygon([impact_area])
        
        # Calculate affected population
        affected_regions = Region.objects.filter(
            geometry__intersects=impact_area
        ).annotate(
            intersection_area=Area(Intersection('geometry', impact_area))
        )
        
        total_affected = 0
        for region in affected_regions:
            # Calculate proportion of region affected
            region_area = region.geometry.area
            proportion = region.intersection_area / region_area
            # Estimate affected population
            total_affected += int(region.population * proportion)
        
        # Find affected assets
        affected_assets = Asset.objects.filter(
            location__intersects=impact_area
        )
        
        # Create or update impact zone
        impact_zone, _ = ImpactZone.objects.update_or_create(
            event=event,
            defaults={
                'geometry': impact_area,
                'severity': event.severity,
                'population_affected': total_affected,
            }
        )
        
        # Update affected assets
        impact_zone.assets_affected.set(affected_assets)
        
    except Event.DoesNotExist:
        print(f"Event {event_id} not found")
    except Exception as e:
        print(f"Error calculating impact zone: {str(e)}")

@shared_task
def assess_infrastructure_impact(impact_zone_id):
    """Assess the impact on critical infrastructure"""
    try:
        impact_zone = ImpactZone.objects.get(id=impact_zone_id)
        
        # Get affected assets by type
        asset_impact = {}
        for asset_type, _ in Asset.ASSET_TYPES:
            affected = impact_zone.assets_affected.filter(
                asset_type=asset_type
            ).count()
            
            if affected > 0:
                asset_impact[asset_type] = {
                    'affected_count': affected,
                    'severity': 'high' if affected > 5 else 'medium' if affected > 2 else 'low'
                }
        
        # Update impact zone metadata
        impact_zone.metadata['infrastructure_impact'] = asset_impact
        impact_zone.save()
        
    except ImpactZone.DoesNotExist:
        print(f"Impact Zone {impact_zone_id} not found")
    except Exception as e:
        print(f"Error assessing infrastructure impact: {str(e)}")

@shared_task
def update_asset_status(asset_id, status):
    """Update the operational status of an asset"""
    try:
        asset = Asset.objects.get(id=asset_id)
        asset.status = status
        asset.save()
        
        # If asset is non-operational, find alternatives
        if status != 'operational':
            find_alternative_assets.delay(asset_id)
            
    except Asset.DoesNotExist:
        print(f"Asset {asset_id} not found")

@shared_task
def find_alternative_assets(asset_id):
    """Find alternative assets when one becomes non-operational"""
    try:
        asset = Asset.objects.get(id=asset_id)
        
        # Find nearest operational assets of the same type
        alternatives = Asset.objects.filter(
            asset_type=asset.asset_type,
            status='operational'
        ).exclude(id=asset_id).order_by(
            Distance('location', asset.location)
        )[:5]
        
        # Update the original asset's metadata with alternatives
        asset.metadata['alternatives'] = [
            {
                'id': alt.id,
                'name': alt.name,
                'distance': alt.distance.km
            }
            for alt in alternatives
        ]
        asset.save()
        
    except Asset.DoesNotExist:
        print(f"Asset {asset_id} not found")
