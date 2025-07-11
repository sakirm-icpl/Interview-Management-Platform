"""
Admin configuration for core models.
"""
from django.contrib import admin
from .models import Department, Skill, FileUpload, Notification, AuditLog, SystemSettings


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['name']


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'created_at']
    list_filter = ['category', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['name']


@admin.register(FileUpload)
class FileUploadAdmin(admin.ModelAdmin):
    list_display = ['original_filename', 'uploaded_by', 'file_size', 'created_at']
    list_filter = ['content_type', 'created_at']
    search_fields = ['original_filename', 'uploaded_by__email']
    readonly_fields = ['file_size', 'content_type']
    ordering = ['-created_at']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'recipient', 'notification_type', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['title', 'message', 'recipient__email']
    readonly_fields = ['sent_at']
    ordering = ['-created_at']


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['action', 'user', 'model_name', 'created_at']
    list_filter = ['action', 'model_name', 'created_at']
    search_fields = ['action', 'user__email', 'model_name']
    readonly_fields = ['ip_address', 'details']
    ordering = ['-created_at']


@admin.register(SystemSettings)
class SystemSettingsAdmin(admin.ModelAdmin):
    list_display = ['key', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['key', 'description']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['key']