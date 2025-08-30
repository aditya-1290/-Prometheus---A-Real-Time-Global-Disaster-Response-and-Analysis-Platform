from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import EventViewSet, SignalViewSet, CorrelationViewSet

router = DefaultRouter()
router.register(r'events', EventViewSet)
router.register(r'signals', SignalViewSet)
router.register(r'correlations', CorrelationViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
