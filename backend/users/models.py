"""
User models for Interview Management Platform.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from core.models import BaseModel, Department, Skill
import uuid


class User(AbstractUser, BaseModel):
    """Custom user model with role-based authentication."""
    
    USER_ROLES = [
        ('admin', 'Admin'),
        ('hr', 'HR Manager'),
        ('interviewer', 'Interviewer'),
        ('candidate', 'Candidate'),
    ]
    
    # Override id to use UUID
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Basic fields
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=USER_ROLES, default='candidate')
    phone_number = models.CharField(max_length=20, blank=True)
    
    # Profile fields
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    bio = models.TextField(blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    
    # Professional fields
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    job_title = models.CharField(max_length=100, blank=True)
    skills = models.ManyToManyField(Skill, blank=True)
    experience_years = models.PositiveIntegerField(default=0)
    education = models.TextField(blank=True)
    certifications = models.TextField(blank=True)
    
    # Account status
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    
    # Email verification
    email_verification_token = models.UUIDField(null=True, blank=True)
    email_verification_expires = models.DateTimeField(null=True, blank=True)
    
    # Password reset
    password_reset_token = models.UUIDField(null=True, blank=True)
    password_reset_expires = models.DateTimeField(null=True, blank=True)
    
    # Social login
    google_id = models.CharField(max_length=100, blank=True)
    linkedin_id = models.CharField(max_length=100, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"
    
    def get_full_name(self):
        """Return the full name of the user."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.email
    
    def is_hr_or_admin(self):
        """Check if user is HR or admin."""
        return self.role in ['admin', 'hr']
    
    def is_interviewer(self):
        """Check if user is an interviewer."""
        return self.role in ['admin', 'hr', 'interviewer']
    
    def is_candidate(self):
        """Check if user is a candidate."""
        return self.role == 'candidate'
    
    def get_role_display_name(self):
        """Get human-readable role name."""
        return dict(self.USER_ROLES).get(self.role, self.role.title())


class UserProfile(BaseModel):
    """Extended user profile for additional information."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Professional summary
    professional_summary = models.TextField(blank=True)
    career_objective = models.TextField(blank=True)
    
    # Work preferences
    preferred_work_type = models.CharField(max_length=50, blank=True)  # remote, hybrid, on-site
    preferred_salary_range = models.CharField(max_length=100, blank=True)
    preferred_location = models.CharField(max_length=200, blank=True)
    notice_period = models.CharField(max_length=50, blank=True)
    
    # Social media
    linkedin_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    portfolio_url = models.URLField(blank=True)
    
    # References
    references = models.JSONField(default=list, blank=True)
    
    # Privacy settings
    profile_visibility = models.CharField(
        max_length=20, 
        choices=[
            ('public', 'Public'),
            ('private', 'Private'),
            ('hr_only', 'HR Only'),
        ],
        default='hr_only'
    )
    
    def __str__(self):
        return f"Profile for {self.user.email}"


class UserActivity(BaseModel):
    """Track user activities for analytics."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=50)
    description = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'User Activity'
        verbose_name_plural = 'User Activities'
    
    def __str__(self):
        return f"{self.user.email} - {self.activity_type}"


class UserSession(BaseModel):
    """Track user sessions for security."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    session_key = models.CharField(max_length=40, unique=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    is_active = models.BooleanField(default=True)
    last_activity = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Session for {self.user.email}"


class Invitation(BaseModel):
    """Invitation model for inviting users to the platform."""
    INVITATION_TYPES = [
        ('candidate', 'Candidate'),
        ('interviewer', 'Interviewer'),
        ('hr', 'HR Manager'),
    ]
    
    email = models.EmailField()
    role = models.CharField(max_length=20, choices=INVITATION_TYPES)
    invited_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_invitations')
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    is_accepted = models.BooleanField(default=False)
    accepted_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField()
    message = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Invitation for {self.email} ({self.role})"
    
    def is_expired(self):
        """Check if invitation has expired."""
        return timezone.now() > self.expires_at
    
    def accept(self, user):
        """Accept the invitation."""
        self.is_accepted = True
        self.accepted_at = timezone.now()
        self.save()
        user.role = self.role
        user.save()