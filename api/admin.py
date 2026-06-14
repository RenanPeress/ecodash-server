from django.contrib import admin
from .models import CollectorToken, Analise


@admin.register(CollectorToken)
class CollectorTokenAdmin(admin.ModelAdmin):
    list_display  = ('user', 'token', 'created_at', 'last_used_at')
    search_fields = ('user__username', 'token')
    readonly_fields = ('token', 'created_at', 'last_used_at')


@admin.register(Analise)
class AnaliseAdmin(admin.ModelAdmin):
    list_display   = ('id', 'software_name', 'user', 'grade', 'sci_score', 'energy_kwh', 'region', 'hardware_type', 'created_at')
    list_filter    = ('grade', 'region', 'hardware_type')
    search_fields  = ('software_name', 'user__username')
    readonly_fields = ('created_at',)
    ordering       = ('-created_at',)
