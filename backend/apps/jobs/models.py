"""
Models for the jobs app.
"""

from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from datetime import timedelta


class JobCategory(models.Model):
    """
    Job categories for organizing jobs.
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="Font Awesome icon class")
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'job_category'
        verbose_name = 'Job Category'
        verbose_name_plural = 'Job Categories'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Job(models.Model):
    """
    Job posting model.
    """
    
    class JobType(models.TextChoices):
        FULL_TIME = 'full_time', 'Full Time'
        PART_TIME = 'part_time', 'Part Time'
        CONTRACT = 'contract', 'Contract'
        INTERNSHIP = 'internship', 'Internship'
        FREELANCE = 'freelance', 'Freelance'
    
    class ExperienceLevel(models.TextChoices):
        ENTRY = 'entry', 'Entry Level'
        JUNIOR = 'junior', 'Junior'
        MID = 'mid', 'Mid Level'
        SENIOR = 'senior', 'Senior'
        LEAD = 'lead', 'Lead'
        PRINCIPAL = 'principal', 'Principal'
    
    class WorkLocation(models.TextChoices):
        REMOTE = 'remote', 'Remote'
        ONSITE = 'onsite', 'On-site'
        HYBRID = 'hybrid', 'Hybrid'
    
    # Basic Information
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250, unique=True)
    description = models.TextField()
    short_description = models.CharField(
        max_length=300,
        help_text="Brief description for job listings"
    )
    
    # Job Details
    category = models.ForeignKey(
        JobCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='jobs'
    )
    job_type = models.CharField(
        max_length=20,
        choices=JobType.choices,
        default=JobType.FULL_TIME
    )
    experience_level = models.CharField(
        max_length=20,
        choices=ExperienceLevel.choices,
        default=ExperienceLevel.MID
    )
    work_location = models.CharField(
        max_length=20,
        choices=WorkLocation.choices,
        default=WorkLocation.ONSITE
    )
    
    # Location Information
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    timezone = models.CharField(max_length=50, blank=True)
    
    # Compensation
    salary_min = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)]
    )
    salary_max = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)]
    )
    salary_currency = models.CharField(max_length=3, default='USD')
    salary_frequency = models.CharField(
        max_length=10,
        choices=[
            ('hourly', 'Hourly'),
            ('yearly', 'Yearly'),
            ('monthly', 'Monthly'),
        ],
        default='yearly'
    )
    
    # Requirements
    requirements = models.TextField(help_text="Job requirements and qualifications")
    responsibilities = models.TextField(help_text="Job responsibilities and duties")
    benefits = models.TextField(blank=True, help_text="Benefits and perks")
    
    # Application Settings
    application_deadline = models.DateTimeField(null=True, blank=True)
    max_applications = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Maximum number of applications to accept"
    )
    require_cover_letter = models.BooleanField(default=False)
    require_portfolio = models.BooleanField(default=False)
    
    # AI Screening Settings
    enable_ai_screening = models.BooleanField(
        default=True,
        help_text="Enable AI-powered candidate screening"
    )
    screening_questions = models.JSONField(
        default=list,
        blank=True,
        help_text="Custom screening questions for the AI chatbot"
    )
    
    # Status and Metadata
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    is_urgent = models.BooleanField(default=False)
    
    # Tracking
    view_count = models.PositiveIntegerField(default=0)
    application_count = models.PositiveIntegerField(default=0)
    
    # Relations
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_jobs'
    )
    required_skills = models.ManyToManyField(
        'authentication.Skill',
        through='JobSkill',
        related_name='required_for_jobs'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'job'
        verbose_name = 'Job'
        verbose_name_plural = 'Jobs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['is_active', '-created_at']),
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['job_type', 'work_location']),
        ]
    
    def __str__(self):
        return f"{self.title} at {self.created_by.company or 'Company'}"
    
    @property
    def is_published(self):
        """Check if job is published."""
        return self.published_at is not None and self.is_active
    
    @property
    def is_expired(self):
        """Check if application deadline has passed."""
        if self.application_deadline:
            return timezone.now() > self.application_deadline
        return False
    
    @property
    def can_accept_applications(self):
        """Check if job can accept new applications."""
        if not self.is_active or self.is_expired:
            return False
        
        if self.max_applications and self.application_count >= self.max_applications:
            return False
        
        return True
    
    @property
    def salary_range(self):
        """Get formatted salary range."""
        if self.salary_min and self.salary_max:
            return f"{self.salary_currency} {self.salary_min:,.0f} - {self.salary_max:,.0f} {self.salary_frequency}"
        elif self.salary_min:
            return f"{self.salary_currency} {self.salary_min:,.0f}+ {self.salary_frequency}"
        return "Salary not specified"
    
    def increment_view_count(self):
        """Increment view count."""
        self.view_count += 1
        self.save(update_fields=['view_count'])
    
    def publish(self):
        """Publish the job."""
        if not self.published_at:
            self.published_at = timezone.now()
            self.save(update_fields=['published_at'])


class JobSkill(models.Model):
    """
    Through model for Job-Skill relationship with importance level.
    """
    
    class ImportanceLevel(models.TextChoices):
        REQUIRED = 'required', 'Required'
        PREFERRED = 'preferred', 'Preferred'
        NICE_TO_HAVE = 'nice_to_have', 'Nice to Have'
    
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    skill = models.ForeignKey('authentication.Skill', on_delete=models.CASCADE)
    importance = models.CharField(
        max_length=20,
        choices=ImportanceLevel.choices,
        default=ImportanceLevel.REQUIRED
    )
    min_experience_years = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Minimum years of experience required for this skill"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'job_skill'
        unique_together = ['job', 'skill']
        ordering = ['importance', 'skill__name']
    
    def __str__(self):
        return f"{self.job.title} - {self.skill.name} ({self.get_importance_display()})"


class JobApplication(models.Model):
    """
    Job application model.
    """
    
    class ApplicationStatus(models.TextChoices):
        PENDING = 'pending', 'Pending Review'
        SCREENING = 'screening', 'AI Screening'
        UNDER_REVIEW = 'under_review', 'Under Review'
        SHORTLISTED = 'shortlisted', 'Shortlisted'
        INTERVIEW_SCHEDULED = 'interview_scheduled', 'Interview Scheduled'
        INTERVIEWED = 'interviewed', 'Interviewed'
        OFFERED = 'offered', 'Offered'
        HIRED = 'hired', 'Hired'
        REJECTED = 'rejected', 'Rejected'
        WITHDRAWN = 'withdrawn', 'Withdrawn'
    
    # Basic Information
    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name='applications'
    )
    candidate = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='job_applications'
    )
    
    # Application Data
    cover_letter = models.TextField(blank=True)
    custom_resume = models.FileField(
        upload_to='application_resumes/',
        blank=True,
        null=True,
        help_text="Custom resume for this application"
    )
    portfolio_url = models.URLField(blank=True)
    additional_info = models.TextField(
        blank=True,
        help_text="Additional information from the candidate"
    )
    
    # Status and Tracking
    status = models.CharField(
        max_length=20,
        choices=ApplicationStatus.choices,
        default=ApplicationStatus.PENDING
    )
    
    # AI Screening Results
    ai_screening_completed = models.BooleanField(default=False)
    ai_screening_score = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    ai_screening_summary = models.TextField(blank=True)
    ai_screening_data = models.JSONField(
        default=dict,
        blank=True,
        help_text="Raw AI screening conversation data"
    )
    
    # HR Notes and Feedback
    hr_notes = models.TextField(blank=True)
    rejection_reason = models.TextField(blank=True)
    
    # Timestamps
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'job_application'
        verbose_name = 'Job Application'
        verbose_name_plural = 'Job Applications'
        unique_together = ['job', 'candidate']
        ordering = ['-applied_at']
        indexes = [
            models.Index(fields=['status', '-applied_at']),
            models.Index(fields=['job', 'status']),
            models.Index(fields=['candidate', '-applied_at']),
        ]
    
    def __str__(self):
        return f"{self.candidate.full_name} - {self.job.title}"
    
    @property
    def can_withdraw(self):
        """Check if application can be withdrawn."""
        return self.status in [
            self.ApplicationStatus.PENDING,
            self.ApplicationStatus.SCREENING,
            self.ApplicationStatus.UNDER_REVIEW,
        ]
    
    @property
    def is_active(self):
        """Check if application is still active."""
        return self.status not in [
            self.ApplicationStatus.REJECTED,
            self.ApplicationStatus.WITHDRAWN,
            self.ApplicationStatus.HIRED,
        ]
    
    def update_status(self, new_status, notes=""):
        """Update application status with optional notes."""
        old_status = self.status
        self.status = new_status
        self.updated_at = timezone.now()
        
        if new_status in [
            self.ApplicationStatus.UNDER_REVIEW,
            self.ApplicationStatus.SHORTLISTED,
        ] and not self.reviewed_at:
            self.reviewed_at = timezone.now()
        
        if notes:
            self.hr_notes = f"{self.hr_notes}\n\n{timezone.now().strftime('%Y-%m-%d %H:%M')}: {notes}".strip()
        
        self.save()
        
        # Create status change history
        ApplicationStatusHistory.objects.create(
            application=self,
            old_status=old_status,
            new_status=new_status,
            notes=notes
        )


class ApplicationStatusHistory(models.Model):
    """
    Track application status changes.
    """
    application = models.ForeignKey(
        JobApplication,
        on_delete=models.CASCADE,
        related_name='status_history'
    )
    old_status = models.CharField(
        max_length=20,
        choices=JobApplication.ApplicationStatus.choices
    )
    new_status = models.CharField(
        max_length=20,
        choices=JobApplication.ApplicationStatus.choices
    )
    notes = models.TextField(blank=True)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    changed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'application_status_history'
        verbose_name = 'Application Status History'
        verbose_name_plural = 'Application Status Histories'
        ordering = ['-changed_at']
    
    def __str__(self):
        return f"{self.application} - {self.old_status} → {self.new_status}"


class SavedJob(models.Model):
    """
    Jobs saved by candidates.
    """
    candidate = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='saved_jobs'
    )
    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name='saved_by'
    )
    saved_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'saved_job'
        unique_together = ['candidate', 'job']
        ordering = ['-saved_at']
    
    def __str__(self):
        return f"{self.candidate.full_name} saved {self.job.title}"


class JobAlert(models.Model):
    """
    Job alerts for candidates.
    """
    candidate = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='job_alerts'
    )
    
    # Alert Criteria
    keywords = models.CharField(max_length=200, blank=True)
    category = models.ForeignKey(
        JobCategory,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    job_type = models.CharField(
        max_length=20,
        choices=Job.JobType.choices,
        blank=True
    )
    work_location = models.CharField(
        max_length=20,
        choices=Job.WorkLocation.choices,
        blank=True
    )
    location = models.CharField(max_length=200, blank=True)
    salary_min = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    # Settings
    is_active = models.BooleanField(default=True)
    frequency = models.CharField(
        max_length=10,
        choices=[
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
            ('monthly', 'Monthly'),
        ],
        default='weekly'
    )
    
    # Tracking
    last_sent = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'job_alert'
        verbose_name = 'Job Alert'
        verbose_name_plural = 'Job Alerts'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Job Alert for {self.candidate.full_name}"
    
    def should_send_alert(self):
        """Check if alert should be sent based on frequency."""
        if not self.is_active:
            return False
        
        if not self.last_sent:
            return True
        
        now = timezone.now()
        if self.frequency == 'daily':
            return now > self.last_sent + timedelta(days=1)
        elif self.frequency == 'weekly':
            return now > self.last_sent + timedelta(weeks=1)
        elif self.frequency == 'monthly':
            return now > self.last_sent + timedelta(days=30)
        
        return False