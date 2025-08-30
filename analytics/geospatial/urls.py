from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import RegionViewSet, RiskZoneViewSet, AssetViewSet, ImpactZoneViewSet

router = DefaultRouter()
router.register(r'regions', RegionViewSet)
router.register(r'risk-zones', RiskZoneViewSet)
router.register(r'assets', AssetViewSet)
router.register(r'impact-zones', ImpactZoneViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
