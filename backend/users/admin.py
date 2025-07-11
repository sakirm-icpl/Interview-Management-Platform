"""
Admin configuration for users app.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserProfile, UserActivity, Invitation


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin configuration for User model."""
    list_display = ['email', 'first_name', 'last_name', 'role', 'is_verified', 'is_active', 'created_at']
    list_filter = ['role', 'is_verified', 'is_active', 'created_at', 'department']
    search_fields = ['email', 'first_name', 'last_name', 'username']
    ordering = ['-created_at']
    
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'phone_number', 'profile_picture', 'bio')}),
        ('Professional info', {'fields': ('role', 'department', 'job_title', 'skills', 'experience_years', 'education', 'certifications')}),
        ('Location', {'fields': ('address', 'city', 'state', 'country', 'postal_code')}),
        ('Account status', {'fields': ('is_verified', 'is_active', 'is_staff', 'is_superuser')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Permissions', {'fields': ('groups', 'user_permissions')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'first_name', 'last_name', 'password1', 'password2', 'role'),
        }),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin configuration for UserProfile model."""
    list_display = ['user', 'profile_visibility', 'preferred_work_type', 'created_at']
    list_filter = ['profile_visibility', 'preferred_work_type', 'created_at']
    search_fields = ['user__email', 'user__first_name', 'user__last_name']
    ordering = ['-created_at']


@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    """Admin configuration for UserActivity model."""
    list_display = ['user', 'activity_type', 'ip_address', 'created_at']
    list_filter = ['activity_type', 'created_at']
    search_fields = ['user__email', 'description']
    readonly_fields = ['ip_address', 'user_agent', 'metadata']
    ordering = ['-created_at']


@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    """Admin configuration for Invitation model."""
    list_display = ['email', 'role', 'invited_by', 'is_accepted', 'expires_at', 'created_at']
    list_filter = ['role', 'is_accepted', 'created_at']
    search_fields = ['email', 'invited_by__email']
    readonly_fields = ['token', 'accepted_at']
    ordering = ['-created_at']