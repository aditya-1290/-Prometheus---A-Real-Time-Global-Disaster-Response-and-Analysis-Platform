from django.contrib import admin
from .models import ServiceHealth, PerformanceMetric, AlertLog

@admin.register(ServiceHealth)
class ServiceHealthAdmin(admin.ModelAdmin):
    list_display = ('name', 'service_type', 'status', 'last_check', 'error_count')
    list_filter = ('service_type', 'status')
    search_fields = ('name',)
    readonly_fields = ('last_check',)

@admin.register(PerformanceMetric)
class PerformanceMetricAdmin(admin.ModelAdmin):
    list_display = ('service', 'metric_type', 'value', 'timestamp')
    list_filter = ('service', 'metric_type')
    date_hierarchy = 'timestamp'

@admin.register(AlertLog)
class AlertLogAdmin(admin.ModelAdmin):
    list_display = ('service', 'severity', 'message', 'timestamp', 'resolved')
    list_filter = ('service', 'severity', 'resolved')
    search_fields = ('message',)
    date_hierarchy = 'timestamp'
    readonly_fields = ('timestamp',)
