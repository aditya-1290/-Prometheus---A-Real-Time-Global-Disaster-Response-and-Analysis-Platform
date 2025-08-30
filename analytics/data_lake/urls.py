from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import (
    DataSourceViewSet, DatasetViewSet,
    DatasetVersionViewSet, ProcessingJobViewSet
)

router = DefaultRouter()
router.register(r'sources', DataSourceViewSet)
router.register(r'datasets', DatasetViewSet)
router.register(r'versions', DatasetVersionViewSet)
router.register(r'jobs', ProcessingJobViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
