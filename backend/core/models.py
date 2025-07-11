"""
Core models for Interview Management Platform.
"""
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()


class TimeStampedModel(models.Model):
    """Abstract base model with created and updated timestamps."""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UUIDModel(models.Model):
    """Abstract base model with UUID primary key."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class BaseModel(TimeStampedModel, UUIDModel):
    """Base model with timestamps and UUID primary key."""
    
    class Meta:
        abstract = True


class Department(BaseModel):
    """Department model for organizing jobs and users."""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']


class Skill(BaseModel):
    """Skill model for job requirements and candidate profiles."""
    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']


class FileUpload(BaseModel):
    """Generic file upload model."""
    file = models.FileField(upload_to='uploads/%Y/%m/%d/')
    original_filename = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField()
    content_type = models.CharField(max_length=100)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.original_filename} ({self.uploaded_by.email})"
    
    class Meta:
        ordering = ['-created_at']


class Notification(BaseModel):
    """Notification model for system notifications."""
    NOTIFICATION_TYPES = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('in_app', 'In-App'),
    ]
    
    recipient = models.ForeignKey(User, on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=10, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.title} - {self.recipient.email}"
    
    class Meta:
        ordering = ['-created_at']


class AuditLog(BaseModel):
    """Audit log for tracking important actions."""
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=100)
    model_name = models.CharField(max_length=100)
    object_id = models.CharField(max_length=100)
    details = models.JSONField(default=dict)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.action} on {self.model_name} by {self.user}"
    
    class Meta:
        ordering = ['-created_at']


class SystemSettings(BaseModel):
    """System-wide settings configuration."""
    key = models.CharField(max_length=100, unique=True)
    value = models.JSONField()
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.key
    
    class Meta:
        ordering = ['key']