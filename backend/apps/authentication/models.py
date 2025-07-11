"""
Authentication models for the Interview Management Platform.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator


class User(AbstractUser):
    """
    Custom User model with role-based authentication.
    """
    
    class UserRole(models.TextChoices):
        ADMIN = 'admin', 'Admin'
        HR = 'hr', 'HR Manager'
        CANDIDATE = 'candidate', 'Candidate'
    
    # Remove username field and use email as the unique identifier
    username = None
    email = models.EmailField('Email Address', unique=True)
    
    # Role-based authentication
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.CANDIDATE,
        help_text='User role determines access permissions'
    )
    
    # Profile information
    phone_number = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
            )
        ]
    )
    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        blank=True,
        null=True,
        help_text='User profile picture'
    )
    date_of_birth = models.DateField(blank=True, null=True)
    
    # Professional information
    company = models.CharField(max_length=100, blank=True, null=True)
    job_title = models.CharField(max_length=100, blank=True, null=True)
    
    # Account status
    is_verified = models.BooleanField(
        default=False,
        help_text='Designates whether this user account is verified.'
    )
    is_phone_verified = models.BooleanField(
        default=False,
        help_text='Designates whether the phone number is verified.'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_activity = models.DateTimeField(blank=True, null=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    class Meta:
        db_table = 'auth_user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.email} ({self.get_role_display()})"
    
    @property
    def full_name(self):
        """Return the user's full name."""
        return f"{self.first_name} {self.last_name}".strip()
    
    @property
    def is_hr_or_admin(self):
        """Check if user is HR manager or admin."""
        return self.role in [self.UserRole.HR, self.UserRole.ADMIN]
    
    @property
    def is_candidate(self):
        """Check if user is a candidate."""
        return self.role == self.UserRole.CANDIDATE
    
    def get_initials(self):
        """Get user initials for display purposes."""
        if self.first_name and self.last_name:
            return f"{self.first_name[0]}{self.last_name[0]}".upper()
        return self.email[0].upper() if self.email else "U"


class UserProfile(models.Model):
    """
    Extended profile information for users.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    
    # Additional personal information
    bio = models.TextField(max_length=500, blank=True)
    linkedin_url = models.URLField(blank=True, null=True)
    github_url = models.URLField(blank=True, null=True)
    portfolio_url = models.URLField(blank=True, null=True)
    
    # Location information
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    
    # Experience and skills (for candidates)
    years_of_experience = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text='Total years of professional experience'
    )
    current_salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text='Current annual salary'
    )
    expected_salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text='Expected annual salary'
    )
    
    # Resume and documents
    resume = models.FileField(
        upload_to='resumes/',
        blank=True,
        null=True,
        help_text='User resume in PDF format'
    )
    cover_letter = models.FileField(
        upload_to='cover_letters/',
        blank=True,
        null=True,
        help_text='Cover letter in PDF format'
    )
    
    # Preferences
    preferred_work_type = models.CharField(
        max_length=20,
        choices=[
            ('remote', 'Remote'),
            ('onsite', 'On-site'),
            ('hybrid', 'Hybrid'),
            ('flexible', 'Flexible')
        ],
        blank=True
    )
    willing_to_relocate = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_profile'
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
    
    def __str__(self):
        return f"Profile of {self.user.email}"


class Skill(models.Model):
    """
    Skills that can be associated with users.
    """
    
    class SkillLevel(models.TextChoices):
        BEGINNER = 'beginner', 'Beginner'
        INTERMEDIATE = 'intermediate', 'Intermediate'
        ADVANCED = 'advanced', 'Advanced'
        EXPERT = 'expert', 'Expert'
    
    class SkillCategory(models.TextChoices):
        PROGRAMMING = 'programming', 'Programming'
        FRAMEWORK = 'framework', 'Framework'
        DATABASE = 'database', 'Database'
        CLOUD = 'cloud', 'Cloud'
        DEVOPS = 'devops', 'DevOps'
        DESIGN = 'design', 'Design'
        SOFT_SKILL = 'soft_skill', 'Soft Skill'
        LANGUAGE = 'language', 'Language'
        CERTIFICATION = 'certification', 'Certification'
        OTHER = 'other', 'Other'
    
    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(
        max_length=20,
        choices=SkillCategory.choices,
        default=SkillCategory.OTHER
    )
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'skill'
        verbose_name = 'Skill'
        verbose_name_plural = 'Skills'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"


class UserSkill(models.Model):
    """
    Through model for User-Skill relationship with proficiency level.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='skills'
    )
    skill = models.ForeignKey(
        Skill,
        on_delete=models.CASCADE,
        related_name='users'
    )
    level = models.CharField(
        max_length=20,
        choices=Skill.SkillLevel.choices,
        default=Skill.SkillLevel.BEGINNER
    )
    years_of_experience = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text='Years of experience with this skill'
    )
    is_primary = models.BooleanField(
        default=False,
        help_text='Mark as primary skill for the user'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_skill'
        verbose_name = 'User Skill'
        verbose_name_plural = 'User Skills'
        unique_together = ['user', 'skill']
        ordering = ['-is_primary', '-years_of_experience', 'skill__name']
    
    def __str__(self):
        return f"{self.user.email} - {self.skill.name} ({self.get_level_display()})"