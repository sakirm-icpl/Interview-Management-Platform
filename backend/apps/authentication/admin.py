"""
Django admin configuration for authentication models.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User, UserProfile, Skill, UserSkill


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Admin configuration for User model.
    """
    list_display = [
        'email', 'full_name', 'role', 'is_verified', 'is_active', 
        'created_at', 'last_login'
    ]
    list_filter = [
        'role', 'is_verified', 'is_phone_verified', 'is_active', 
        'is_staff', 'created_at'
    ]
    search_fields = ['email', 'first_name', 'last_name', 'company']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at', 'last_login', 'last_activity']
    
    fieldsets = (
        (None, {
            'fields': ('email', 'password')
        }),
        ('Personal info', {
            'fields': (
                'first_name', 'last_name', 'phone_number', 
                'profile_picture', 'date_of_birth'
            )
        }),
        ('Professional info', {
            'fields': ('company', 'job_title')
        }),
        ('Permissions', {
            'fields': (
                'role', 'is_active', 'is_staff', 'is_superuser',
                'is_verified', 'is_phone_verified', 'groups', 'user_permissions'
            ),
        }),
        ('Important dates', {
            'fields': ('last_login', 'created_at', 'updated_at', 'last_activity')
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'first_name', 'last_name', 'role', 
                'password1', 'password2'
            ),
        }),
    )
    
    def full_name(self, obj):
        """Display full name in list."""
        return obj.full_name or '-'
    full_name.short_description = 'Full Name'
    
    def get_queryset(self, request):
        """Optimize queryset with related fields."""
        return super().get_queryset(request).select_related('profile')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """
    Admin configuration for UserProfile model.
    """
    list_display = [
        'user_email', 'user_role', 'years_of_experience', 
        'preferred_work_type', 'willing_to_relocate', 'has_resume'
    ]
    list_filter = [
        'preferred_work_type', 'willing_to_relocate', 
        'user__role', 'created_at'
    ]
    search_fields = [
        'user__email', 'user__first_name', 'user__last_name',
        'bio', 'city', 'state', 'country'
    ]
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Personal Information', {
            'fields': (
                'bio', 'linkedin_url', 'github_url', 'portfolio_url'
            )
        }),
        ('Location', {
            'fields': (
                'address', 'city', 'state', 'country', 'postal_code'
            )
        }),
        ('Professional Information', {
            'fields': (
                'years_of_experience', 'current_salary', 'expected_salary'
            )
        }),
        ('Documents', {
            'fields': ('resume', 'cover_letter')
        }),
        ('Preferences', {
            'fields': ('preferred_work_type', 'willing_to_relocate')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def user_email(self, obj):
        """Display user email."""
        return obj.user.email
    user_email.short_description = 'Email'
    user_email.admin_order_field = 'user__email'
    
    def user_role(self, obj):
        """Display user role."""
        return obj.user.get_role_display()
    user_role.short_description = 'Role'
    user_role.admin_order_field = 'user__role'
    
    def has_resume(self, obj):
        """Check if user has uploaded resume."""
        return bool(obj.resume)
    has_resume.boolean = True
    has_resume.short_description = 'Resume'


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    """
    Admin configuration for Skill model.
    """
    list_display = ['name', 'category', 'is_active', 'users_count', 'created_at']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['category', 'name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        (None, {
            'fields': ('name', 'category', 'description', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def users_count(self, obj):
        """Count users with this skill."""
        return obj.users.count()
    users_count.short_description = 'Users Count'
    
    def get_queryset(self, request):
        """Optimize queryset with prefetch."""
        return super().get_queryset(request).prefetch_related('users')


@admin.register(UserSkill)
class UserSkillAdmin(admin.ModelAdmin):
    """
    Admin configuration for UserSkill model.
    """
    list_display = [
        'user_email', 'skill_name', 'level', 'years_of_experience', 
        'is_primary', 'created_at'
    ]
    list_filter = ['level', 'is_primary', 'skill__category', 'created_at']
    search_fields = [
        'user__email', 'user__first_name', 'user__last_name',
        'skill__name'
    ]
    ordering = ['-is_primary', '-years_of_experience', 'skill__name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        (None, {
            'fields': ('user', 'skill', 'level', 'years_of_experience', 'is_primary')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def user_email(self, obj):
        """Display user email."""
        return obj.user.email
    user_email.short_description = 'User Email'
    user_email.admin_order_field = 'user__email'
    
    def skill_name(self, obj):
        """Display skill name."""
        return obj.skill.name
    skill_name.short_description = 'Skill'
    skill_name.admin_order_field = 'skill__name'
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related('user', 'skill')


# Customize admin site header and title
admin.site.site_header = "Interview Management Platform Admin"
admin.site.site_title = "Interview Platform Admin"
admin.site.index_title = "Welcome to Interview Management Platform"