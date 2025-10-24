from django.contrib import admin
from .models import Summary

@admin.register(Summary)
class SummaryAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'created_at', 'updated_at', 'is_public')
    list_filter = ('is_public', 'created_at', 'updated_at')
    search_fields = ('title', 'user__username', 'original_text')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Summary Information', {
            'fields': ('user', 'title', 'original_text', 'summary_text', 'is_public')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
