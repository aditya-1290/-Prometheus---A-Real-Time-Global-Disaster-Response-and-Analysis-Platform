from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .serializers import (
    DisasterConfigSerializer,
    ResourceTypeSerializer,
    AlertConfigSerializer,
    SystemConfigSerializer
)
from .models import (
    DisasterConfig,
    ResourceType,
    AlertConfig,
    SystemConfig
)

class DisasterConfigViewSet(viewsets.ModelViewSet):
    queryset = DisasterConfig.objects.all()
    serializer_class = DisasterConfigSerializer
    permission_classes = [IsAuthenticated]

class ResourceTypeViewSet(viewsets.ModelViewSet):
    queryset = ResourceType.objects.all()
    serializer_class = ResourceTypeSerializer
    permission_classes = [IsAuthenticated]

class AlertConfigViewSet(viewsets.ModelViewSet):
    queryset = AlertConfig.objects.all()
    serializer_class = AlertConfigSerializer
    permission_classes = [IsAuthenticated]

class SystemConfigViewSet(viewsets.ModelViewSet):
    queryset = SystemConfig.objects.all()
    serializer_class = SystemConfigSerializer
    permission_classes = [IsAuthenticated]
