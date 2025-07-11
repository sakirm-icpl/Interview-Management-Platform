"""
Models for the AI chatbot screening system.
"""

from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import uuid


class ChatSession(models.Model):
    """
    Chat session for AI-powered candidate screening.
    """
    
    class SessionStatus(models.TextChoices):
        ACTIVE = 'active', 'Active'
        COMPLETED = 'completed', 'Completed'
        ABANDONED = 'abandoned', 'Abandoned'
        ERROR = 'error', 'Error'
    
    # Unique session identifier
    session_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    
    # Related models
    job_application = models.ForeignKey(
        'jobs.JobApplication',
        on_delete=models.CASCADE,
        related_name='chat_sessions'
    )
    candidate = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='chat_sessions'
    )
    job = models.ForeignKey(
        'jobs.Job',
        on_delete=models.CASCADE,
        related_name='chat_sessions'
    )
    
    # Session metadata
    status = models.CharField(
        max_length=20,
        choices=SessionStatus.choices,
        default=SessionStatus.ACTIVE
    )
    
    # AI Configuration
    ai_model = models.CharField(max_length=50, default='gpt-4')
    language = models.CharField(max_length=10, default='en')
    
    # Session Progress
    current_question_index = models.PositiveIntegerField(default=0)
    total_questions = models.PositiveIntegerField(default=0)
    questions_answered = models.PositiveIntegerField(default=0)
    
    # Scoring and Analysis
    overall_score = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    technical_score = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    communication_score = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    culture_fit_score = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    
    # AI-generated summary
    summary = models.TextField(blank=True)
    recommendations = models.TextField(blank=True)
    red_flags = models.JSONField(default=list, blank=True)
    strengths = models.JSONField(default=list, blank=True)
    
    # Session timing
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    last_activity = models.DateTimeField(auto_now=True)
    duration_minutes = models.PositiveIntegerField(null=True, blank=True)
    
    # Configuration used for this session
    session_config = models.JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'chat_session'
        verbose_name = 'Chat Session'
        verbose_name_plural = 'Chat Sessions'
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['candidate', '-started_at']),
            models.Index(fields=['job', '-started_at']),
            models.Index(fields=['status', '-started_at']),
        ]
    
    def __str__(self):
        return f"Chat Session {self.session_id} - {self.candidate.full_name}"
    
    @property
    def is_active(self):
        """Check if session is currently active."""
        return self.status == self.SessionStatus.ACTIVE
    
    @property
    def progress_percentage(self):
        """Calculate session progress percentage."""
        if self.total_questions == 0:
            return 0
        return (self.questions_answered / self.total_questions) * 100
    
    def complete_session(self):
        """Mark session as completed and calculate final scores."""
        self.status = self.SessionStatus.COMPLETED
        self.completed_at = timezone.now()
        
        if self.started_at and self.completed_at:
            duration = self.completed_at - self.started_at
            self.duration_minutes = int(duration.total_seconds() / 60)
        
        self.save()
    
    def abandon_session(self):
        """Mark session as abandoned."""
        self.status = self.SessionStatus.ABANDONED
        self.save()


class ChatMessage(models.Model):
    """
    Individual messages in a chat session.
    """
    
    class MessageType(models.TextChoices):
        SYSTEM = 'system', 'System Message'
        AI_QUESTION = 'ai_question', 'AI Question'
        USER_RESPONSE = 'user_response', 'User Response'
        AI_FOLLOWUP = 'ai_followup', 'AI Follow-up'
        CLARIFICATION = 'clarification', 'Clarification Request'
    
    # Relations
    session = models.ForeignKey(
        ChatSession,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    
    # Message data
    message_type = models.CharField(
        max_length=20,
        choices=MessageType.choices,
        default=MessageType.AI_QUESTION
    )
    content = models.TextField()
    
    # AI metadata
    ai_prompt = models.TextField(blank=True)
    ai_response_data = models.JSONField(default=dict, blank=True)
    tokens_used = models.PositiveIntegerField(null=True, blank=True)
    
    # Message analysis
    sentiment_score = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(-1), MaxValueValidator(1)]
    )
    confidence_score = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(1)]
    )
    keywords = models.JSONField(default=list, blank=True)
    
    # Timing
    timestamp = models.DateTimeField(auto_now_add=True)
    response_time_seconds = models.PositiveIntegerField(null=True, blank=True)
    
    # Question-specific data
    question_category = models.CharField(max_length=50, blank=True)
    question_difficulty = models.CharField(
        max_length=10,
        choices=[
            ('easy', 'Easy'),
            ('medium', 'Medium'),
            ('hard', 'Hard'),
        ],
        blank=True
    )
    expected_answer_type = models.CharField(max_length=50, blank=True)
    
    class Meta:
        db_table = 'chat_message'
        verbose_name = 'Chat Message'
        verbose_name_plural = 'Chat Messages'
        ordering = ['timestamp']
        indexes = [
            models.Index(fields=['session', 'timestamp']),
            models.Index(fields=['message_type', 'timestamp']),
        ]
    
    def __str__(self):
        return f"Message {self.id} - {self.message_type} in {self.session.session_id}"


class QuestionTemplate(models.Model):
    """
    Templates for AI-generated questions.
    """
    
    class Category(models.TextChoices):
        TECHNICAL = 'technical', 'Technical Skills'
        BEHAVIORAL = 'behavioral', 'Behavioral'
        SITUATIONAL = 'situational', 'Situational'
        CULTURE_FIT = 'culture_fit', 'Culture Fit'
        EXPERIENCE = 'experience', 'Experience'
        MOTIVATION = 'motivation', 'Motivation'
        COMMUNICATION = 'communication', 'Communication'
    
    class Difficulty(models.TextChoices):
        EASY = 'easy', 'Easy'
        MEDIUM = 'medium', 'Medium'
        HARD = 'hard', 'Hard'
    
    # Basic information
    title = models.CharField(max_length=200)
    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        default=Category.BEHAVIORAL
    )
    difficulty = models.CharField(
        max_length=10,
        choices=Difficulty.choices,
        default=Difficulty.MEDIUM
    )
    
    # Template content
    question_template = models.TextField(
        help_text="Question template with placeholders like {skill}, {company}, etc."
    )
    context_prompt = models.TextField(
        blank=True,
        help_text="Additional context for AI to generate the question"
    )
    
    # Configuration
    expected_answer_type = models.CharField(
        max_length=50,
        choices=[
            ('technical', 'Technical Answer'),
            ('example', 'Example/Story'),
            ('opinion', 'Opinion'),
            ('factual', 'Factual'),
            ('open_ended', 'Open Ended'),
        ],
        default='open_ended'
    )
    follow_up_enabled = models.BooleanField(default=True)
    max_follow_ups = models.PositiveIntegerField(default=2)
    
    # Scoring criteria
    scoring_criteria = models.JSONField(
        default=dict,
        blank=True,
        help_text="Criteria for AI to score responses"
    )
    
    # Usage tracking
    usage_count = models.PositiveIntegerField(default=0)
    success_rate = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    
    # Related skills
    related_skills = models.ManyToManyField(
        'authentication.Skill',
        blank=True,
        related_name='question_templates'
    )
    
    # Metadata
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_question_templates'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'question_template'
        verbose_name = 'Question Template'
        verbose_name_plural = 'Question Templates'
        ordering = ['category', 'difficulty', 'title']
        indexes = [
            models.Index(fields=['category', 'difficulty']),
            models.Index(fields=['is_active', '-usage_count']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.get_category_display()} - {self.get_difficulty_display()})"
    
    def increment_usage(self):
        """Increment usage count."""
        self.usage_count += 1
        self.save(update_fields=['usage_count'])


class ScreeningConfiguration(models.Model):
    """
    Configuration for AI screening sessions.
    """
    
    # Basic information
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Target configuration
    job_categories = models.ManyToManyField(
        'jobs.JobCategory',
        blank=True,
        related_name='screening_configs'
    )
    experience_levels = models.JSONField(
        default=list,
        blank=True,
        help_text="List of experience levels this config applies to"
    )
    
    # Question configuration
    total_questions = models.PositiveIntegerField(default=10)
    question_distribution = models.JSONField(
        default=dict,
        blank=True,
        help_text="Distribution of questions by category"
    )
    time_limit_minutes = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Optional time limit for the session"
    )
    
    # AI behavior settings
    ai_personality = models.CharField(
        max_length=50,
        choices=[
            ('professional', 'Professional'),
            ('friendly', 'Friendly'),
            ('casual', 'Casual'),
            ('formal', 'Formal'),
        ],
        default='professional'
    )
    follow_up_probability = models.FloatField(
        default=0.3,
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        help_text="Probability of AI asking follow-up questions"
    )
    clarification_threshold = models.FloatField(
        default=0.5,
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        help_text="Confidence threshold below which AI asks for clarification"
    )
    
    # Scoring configuration
    scoring_weights = models.JSONField(
        default=dict,
        blank=True,
        help_text="Weights for different scoring categories"
    )
    pass_threshold = models.FloatField(
        default=70.0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Minimum score to pass the screening"
    )
    
    # Question templates to use
    question_templates = models.ManyToManyField(
        QuestionTemplate,
        through='ConfigurationQuestionTemplate',
        related_name='screening_configurations'
    )
    
    # Status and metadata
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_screening_configs'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'screening_configuration'
        verbose_name = 'Screening Configuration'
        verbose_name_plural = 'Screening Configurations'
        ordering = ['-is_default', 'name']
    
    def __str__(self):
        return f"{self.name} ({'Default' if self.is_default else 'Custom'})"
    
    def save(self, *args, **kwargs):
        """Ensure only one default configuration exists."""
        if self.is_default:
            ScreeningConfiguration.objects.exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)


class ConfigurationQuestionTemplate(models.Model):
    """
    Through model for ScreeningConfiguration-QuestionTemplate relationship.
    """
    configuration = models.ForeignKey(ScreeningConfiguration, on_delete=models.CASCADE)
    question_template = models.ForeignKey(QuestionTemplate, on_delete=models.CASCADE)
    
    # Template-specific settings for this configuration
    weight = models.FloatField(
        default=1.0,
        validators=[MinValueValidator(0)],
        help_text="Weight of this template in question selection"
    )
    max_questions = models.PositiveIntegerField(
        default=1,
        help_text="Maximum questions to generate from this template"
    )
    is_required = models.BooleanField(
        default=False,
        help_text="Whether this template must be used in every session"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'configuration_question_template'
        unique_together = ['configuration', 'question_template']
        ordering = ['-weight', 'question_template__category']
    
    def __str__(self):
        return f"{self.configuration.name} - {self.question_template.title}"


class ScreeningResult(models.Model):
    """
    Final results and analysis from AI screening.
    """
    
    class Recommendation(models.TextChoices):
        STRONG_PASS = 'strong_pass', 'Strong Pass'
        PASS = 'pass', 'Pass'
        CONDITIONAL_PASS = 'conditional_pass', 'Conditional Pass'
        FAIL = 'fail', 'Fail'
        STRONG_FAIL = 'strong_fail', 'Strong Fail'
    
    # Relations
    session = models.OneToOneField(
        ChatSession,
        on_delete=models.CASCADE,
        related_name='result'
    )
    job_application = models.ForeignKey(
        'jobs.JobApplication',
        on_delete=models.CASCADE,
        related_name='screening_results'
    )
    
    # Overall assessment
    recommendation = models.CharField(
        max_length=20,
        choices=Recommendation.choices,
        null=True,
        blank=True
    )
    confidence_level = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(1)]
    )
    
    # Detailed analysis
    strengths = models.JSONField(default=list, blank=True)
    weaknesses = models.JSONField(default=list, blank=True)
    red_flags = models.JSONField(default=list, blank=True)
    notable_responses = models.JSONField(default=list, blank=True)
    
    # Skills assessment
    skills_assessment = models.JSONField(
        default=dict,
        blank=True,
        help_text="Assessment of candidate skills based on responses"
    )
    
    # AI-generated content
    executive_summary = models.TextField(blank=True)
    detailed_analysis = models.TextField(blank=True)
    interviewer_notes = models.TextField(blank=True)
    next_steps_recommendation = models.TextField(blank=True)
    
    # Metadata
    ai_model_version = models.CharField(max_length=50, blank=True)
    processing_time_seconds = models.PositiveIntegerField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'screening_result'
        verbose_name = 'Screening Result'
        verbose_name_plural = 'Screening Results'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Screening Result for {self.job_application}"