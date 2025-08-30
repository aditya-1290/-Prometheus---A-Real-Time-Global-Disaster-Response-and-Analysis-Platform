from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/correlation/', include('event_correlation.urls')),
    path('api/geo/', include('geospatial.urls')),
    path('api/datalake/', include('data_lake.urls')),
]
