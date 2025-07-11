"""
Serializers for job management and applications.
"""
from rest_framework import serializers
from .models import Job, JobApplication, JobQuestion, ApplicationAnswer, JobBookmark, JobAlert


class JobQuestionSerializer(serializers.ModelSerializer):
    """Serializer for job questions."""
    
    class Meta:
        model = JobQuestion
        fields = '__all__'


class JobSerializer(serializers.ModelSerializer):
    """Main job serializer."""
    department_name = serializers.CharField(source='department.name', read_only=True)
    posted_by_name = serializers.CharField(source='posted_by.get_full_name', read_only=True)
    required_skills = serializers.SlugRelatedField(many=True, slug_field='name', read_only=True)
    preferred_skills = serializers.SlugRelatedField(many=True, slug_field='name', read_only=True)
    questions = JobQuestionSerializer(many=True, read_only=True)
    is_open_for_applications = serializers.ReadOnlyField()
    applications_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Job
        fields = '__all__'
        read_only_fields = ['posted_by', 'views_count', 'applications_count', 'slug']


class JobListSerializer(serializers.ModelSerializer):
    """Serializer for job list views."""
    department_name = serializers.CharField(source='department.name', read_only=True)
    posted_by_name = serializers.CharField(source='posted_by.get_full_name', read_only=True)
    is_open_for_applications = serializers.ReadOnlyField()
    
    class Meta:
        model = Job
        fields = [
            'id', 'title', 'department_name', 'employment_type', 'experience_level',
            'work_model', 'location', 'salary_min', 'salary_max', 'salary_currency',
            'is_open_for_applications', 'posted_by_name', 'created_at', 'views_count',
            'applications_count'
        ]


class JobApplicationSerializer(serializers.ModelSerializer):
    """Serializer for job applications."""
    job_title = serializers.CharField(source='job.title', read_only=True)
    candidate_name = serializers.CharField(source='candidate.get_full_name', read_only=True)
    candidate_email = serializers.CharField(source='candidate.email', read_only=True)
    
    class Meta:
        model = JobApplication
        fields = '__all__'
        read_only_fields = ['candidate', 'status_updated_at', 'status_updated_by']


class JobApplicationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating job applications."""
    
    class Meta:
        model = JobApplication
        fields = ['job', 'cover_letter', 'resume', 'portfolio_url']
    
    def validate_job(self, value):
        """Validate that job is open for applications."""
        if not value.is_open_for_applications():
            raise serializers.ValidationError("This job is not open for applications.")
        return value
    
    def validate(self, attrs):
        """Validate that user hasn't already applied."""
        user = self.context['request'].user
        job = attrs['job']
        
        if JobApplication.objects.filter(job=job, candidate=user).exists():
            raise serializers.ValidationError("You have already applied for this job.")
        
        return attrs


class ApplicationAnswerSerializer(serializers.ModelSerializer):
    """Serializer for application answers."""
    question_text = serializers.CharField(source='question.question_text', read_only=True)
    
    class Meta:
        model = ApplicationAnswer
        fields = '__all__'


class JobBookmarkSerializer(serializers.ModelSerializer):
    """Serializer for job bookmarks."""
    job_title = serializers.CharField(source='job.title', read_only=True)
    
    class Meta:
        model = JobBookmark
        fields = '__all__'
        read_only_fields = ['user']


class JobAlertSerializer(serializers.ModelSerializer):
    """Serializer for job alerts."""
    
    class Meta:
        model = JobAlert
        fields = '__all__'
        read_only_fields = ['user']


class JobSearchSerializer(serializers.Serializer):
    """Serializer for job search parameters."""
    q = serializers.CharField(required=False, help_text="Search query")
    department = serializers.CharField(required=False)
    employment_type = serializers.CharField(required=False)
    experience_level = serializers.CharField(required=False)
    work_model = serializers.CharField(required=False)
    location = serializers.CharField(required=False)
    min_salary = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    max_salary = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    skills = serializers.ListField(child=serializers.CharField(), required=False)
    is_active = serializers.BooleanField(required=False, default=True)


class JobApplicationStatusUpdateSerializer(serializers.Serializer):
    """Serializer for updating application status."""
    status = serializers.ChoiceField(choices=JobApplication.STATUS_CHOICES)
    internal_notes = serializers.CharField(required=False, allow_blank=True)
    interview_feedback = serializers.CharField(required=False, allow_blank=True)
    technical_score = serializers.DecimalField(
        max_digits=5, decimal_places=2, required=False,
        min_value=0, max_value=100
    )
    cultural_fit_score = serializers.DecimalField(
        max_digits=5, decimal_places=2, required=False,
        min_value=0, max_value=100
    )