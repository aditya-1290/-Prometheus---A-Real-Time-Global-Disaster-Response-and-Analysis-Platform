from django.contrib import admin
from .models import APIKey, APIEndpoint, APIUsageLog, WebhookConfig

@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    list_display = ('name', 'key_type', 'active', 'created_at', 'expires_at')
    list_filter = ('key_type', 'active')
    search_fields = ('name',)
    readonly_fields = ('created_at', 'last_used')

@admin.register(APIEndpoint)
class APIEndpointAdmin(admin.ModelAdmin):
    list_display = ('path', 'method', 'requires_auth', 'rate_limit', 'deprecated')
    list_filter = ('method', 'requires_auth', 'deprecated')
    search_fields = ('path', 'description')

@admin.register(APIUsageLog)
class APIUsageLogAdmin(admin.ModelAdmin):
    list_display = ('endpoint', 'api_key', 'timestamp', 'status_code', 'response_time')
    list_filter = ('endpoint', 'status_code')
    date_hierarchy = 'timestamp'
    readonly_fields = ('timestamp',)

@admin.register(WebhookConfig)
class WebhookConfigAdmin(admin.ModelAdmin):
    list_display = ('name', 'event_type', 'active', 'retry_count', 'last_triggered')
    list_filter = ('event_type', 'active')
    search_fields = ('name', 'url')
    readonly_fields = ('created_at', 'last_triggered')
