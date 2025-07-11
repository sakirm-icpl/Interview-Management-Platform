"""
Job models for Interview Management Platform.
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from core.models import BaseModel, Department, Skill
from users.models import User
from django.utils import timezone


class Job(BaseModel):
    """Job posting model."""
    
    EMPLOYMENT_TYPES = [
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contract', 'Contract'),
        ('internship', 'Internship'),
        ('freelance', 'Freelance'),
    ]
    
    EXPERIENCE_LEVELS = [
        ('entry', 'Entry Level'),
        ('junior', 'Junior'),
        ('mid', 'Mid Level'),
        ('senior', 'Senior'),
        ('lead', 'Lead'),
        ('executive', 'Executive'),
    ]
    
    WORK_MODELS = [
        ('remote', 'Remote'),
        ('hybrid', 'Hybrid'),
        ('on_site', 'On-Site'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('closed', 'Closed'),
        ('archived', 'Archived'),
    ]
    
    # Basic information
    title = models.CharField(max_length=200)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    description = models.TextField()
    requirements = models.TextField()
    responsibilities = models.TextField()
    
    # Job details
    employment_type = models.CharField(max_length=20, choices=EMPLOYMENT_TYPES)
    experience_level = models.CharField(max_length=20, choices=EXPERIENCE_LEVELS)
    work_model = models.CharField(max_length=20, choices=WORK_MODELS)
    
    # Location and salary
    location = models.CharField(max_length=200)
    salary_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    salary_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    salary_currency = models.CharField(max_length=3, default='USD')
    is_salary_negotiable = models.BooleanField(default=True)
    
    # Requirements
    required_skills = models.ManyToManyField(Skill, related_name='required_jobs')
    preferred_skills = models.ManyToManyField(Skill, related_name='preferred_jobs', blank=True)
    min_experience_years = models.PositiveIntegerField(default=0)
    education_required = models.CharField(max_length=100, blank=True)
    
    # Application settings
    application_deadline = models.DateTimeField(null=True, blank=True)
    max_applications = models.PositiveIntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Metadata
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posted_jobs')
    views_count = models.PositiveIntegerField(default=0)
    applications_count = models.PositiveIntegerField(default=0)
    
    # SEO and search
    keywords = models.TextField(blank=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def is_open_for_applications(self):
        """Check if job is open for applications."""
        if not self.is_active or self.status != 'published':
            return False
        if self.application_deadline and self.application_deadline < timezone.now():
            return False
        if self.max_applications and self.applications_count >= self.max_applications:
            return False
        return True
    
    def increment_views(self):
        """Increment view count."""
        self.views_count += 1
        self.save(update_fields=['views_count'])


class JobApplication(BaseModel):
    """Job application model."""
    
    STATUS_CHOICES = [
        ('applied', 'Applied'),
        ('screening', 'Screening'),
        ('interview_scheduled', 'Interview Scheduled'),
        ('interviewed', 'Interviewed'),
        ('shortlisted', 'Shortlisted'),
        ('offered', 'Offered'),
        ('hired', 'Hired'),
        ('rejected', 'Rejected'),
        ('withdrawn', 'Withdrawn'),
    ]
    
    # Application details
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    candidate = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')
    
    # Application content
    cover_letter = models.TextField()
    resume = models.FileField(upload_to='resumes/%Y/%m/%d/')
    portfolio_url = models.URLField(blank=True)
    
    # Status and tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='applied')
    status_updated_at = models.DateTimeField(auto_now=True)
    status_updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, 
        related_name='status_updates'
    )
    
    # Assessment
    ai_screening_score = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    ai_screening_summary = models.TextField(blank=True)
    ai_screening_completed = models.BooleanField(default=False)
    
    # Interview feedback
    interview_feedback = models.TextField(blank=True)
    technical_score = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    cultural_fit_score = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    
    # Notes
    internal_notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['job', 'candidate']
    
    def __str__(self):
        return f"{self.candidate.email} - {self.job.title}"
    
    def save(self, *args, **kwargs):
        if self.status == 'applied' and not self.pk:
            # Increment job applications count
            self.job.applications_count += 1
            self.job.save(update_fields=['applications_count'])
        super().save(*args, **kwargs)


class JobQuestion(BaseModel):
    """Custom questions for job applications."""
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    question_type = models.CharField(
        max_length=20,
        choices=[
            ('text', 'Text'),
            ('textarea', 'Long Text'),
            ('multiple_choice', 'Multiple Choice'),
            ('checkbox', 'Checkbox'),
            ('file', 'File Upload'),
        ],
        default='text'
    )
    is_required = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    options = models.JSONField(default=list, blank=True)  # For multiple choice questions
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.job.title} - {self.question_text[:50]}"


class ApplicationAnswer(BaseModel):
    """Answers to job application questions."""
    application = models.ForeignKey(JobApplication, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(JobQuestion, on_delete=models.CASCADE)
    answer_text = models.TextField(blank=True)
    answer_file = models.FileField(upload_to='application_answers/%Y/%m/%d/', blank=True)
    
    class Meta:
        unique_together = ['application', 'question']
    
    def __str__(self):
        return f"{self.application.candidate.email} - {self.question.question_text[:30]}"


class JobBookmark(BaseModel):
    """Job bookmarks for candidates."""
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='bookmarks')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookmarked_jobs')
    
    class Meta:
        unique_together = ['job', 'user']
    
    def __str__(self):
        return f"{self.user.email} bookmarked {self.job.title}"


class JobAlert(BaseModel):
    """Job alerts for candidates."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_alerts')
    title = models.CharField(max_length=200)
    keywords = models.TextField(blank=True)
    location = models.CharField(max_length=200, blank=True)
    employment_type = models.CharField(max_length=20, choices=Job.EMPLOYMENT_TYPES, blank=True)
    experience_level = models.CharField(max_length=20, choices=Job.EXPERIENCE_LEVELS, blank=True)
    is_active = models.BooleanField(default=True)
    frequency = models.CharField(
        max_length=20,
        choices=[
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
            ('monthly', 'Monthly'),
        ],
        default='weekly'
    )
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.title}"