"""
Serializers for authentication app.
"""

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from .models import User, UserProfile, Skill, UserSkill


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    """
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        validators=[validate_password]
    )
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'email', 'password', 'password_confirm', 'first_name', 
            'last_name', 'role', 'phone_number', 'company', 'job_title'
        ]
        extra_kwargs = {
            'role': {'default': User.UserRole.CANDIDATE}
        }
    
    def validate(self, attrs):
        """Validate password confirmation."""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': 'Password fields do not match.'
            })
        return attrs
    
    def validate_email(self, value):
        """Validate email uniqueness."""
        if User.objects.filter(email=value.lower()).exists():
            raise serializers.ValidationError(
                'A user with this email already exists.'
            )
        return value.lower()
    
    def create(self, validated_data):
        """Create new user account."""
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        user = User.objects.create_user(
            password=password,
            **validated_data
        )
        
        # Create user profile
        UserProfile.objects.create(user=user)
        
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom JWT token serializer with additional user data.
    """
    
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        # Add custom claims
        token['email'] = user.email
        token['role'] = user.role
        token['full_name'] = user.full_name
        token['is_verified'] = user.is_verified
        
        return token
    
    def validate(self, attrs):
        """Validate login credentials and check account status."""
        data = super().validate(attrs)
        
        # Add user information to response
        data['user'] = {
            'id': self.user.id,
            'email': self.user.email,
            'role': self.user.role,
            'full_name': self.user.full_name,
            'is_verified': self.user.is_verified,
            'is_active': self.user.is_active,
        }
        
        return data


class SkillSerializer(serializers.ModelSerializer):
    """
    Serializer for skills.
    """
    
    class Meta:
        model = Skill
        fields = [
            'id', 'name', 'category', 'description', 
            'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class UserSkillSerializer(serializers.ModelSerializer):
    """
    Serializer for user skills.
    """
    skill_name = serializers.CharField(source='skill.name', read_only=True)
    skill_category = serializers.CharField(source='skill.category', read_only=True)
    
    class Meta:
        model = UserSkill
        fields = [
            'id', 'skill', 'skill_name', 'skill_category', 
            'level', 'years_of_experience', 'is_primary', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile.
    """
    skills = UserSkillSerializer(source='user.skills', many=True, read_only=True)
    
    class Meta:
        model = UserProfile
        fields = [
            'bio', 'linkedin_url', 'github_url', 'portfolio_url',
            'address', 'city', 'state', 'country', 'postal_code',
            'years_of_experience', 'current_salary', 'expected_salary',
            'resume', 'cover_letter', 'preferred_work_type', 
            'willing_to_relocate', 'skills', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for user data.
    """
    profile = UserProfileSerializer(read_only=True)
    initials = serializers.CharField(source='get_initials', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'role', 'phone_number', 'profile_picture', 'date_of_birth',
            'company', 'job_title', 'is_verified', 'is_phone_verified',
            'is_active', 'last_login', 'created_at', 'updated_at',
            'initials', 'profile'
        ]
        read_only_fields = [
            'id', 'full_name', 'is_verified', 'is_phone_verified',
            'last_login', 'created_at', 'updated_at', 'initials'
        ]


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user information.
    """
    
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'phone_number', 
            'profile_picture', 'date_of_birth', 'company', 'job_title'
        ]
    
    def validate_phone_number(self, value):
        """Validate phone number format."""
        if value and not value.startswith('+'):
            # Add country code if not present
            value = f'+1{value}' if value.isdigit() else value
        return value


class PasswordChangeSerializer(serializers.Serializer):
    """
    Serializer for password change.
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(
        required=True,
        validators=[validate_password]
    )
    new_password_confirm = serializers.CharField(required=True)
    
    def validate(self, attrs):
        """Validate password change data."""
        user = self.context['request'].user
        
        # Check old password
        if not authenticate(
            username=user.email,
            password=attrs['old_password']
        ):
            raise serializers.ValidationError({
                'old_password': 'Incorrect password.'
            })
        
        # Check new password confirmation
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': 'Password fields do not match.'
            })
        
        return attrs


class PasswordResetRequestSerializer(serializers.Serializer):
    """
    Serializer for password reset request.
    """
    email = serializers.EmailField(required=True)
    
    def validate_email(self, value):
        """Validate email exists."""
        try:
            User.objects.get(email=value.lower(), is_active=True)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                'No active account found with this email address.'
            )
        return value.lower()


class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Serializer for password reset confirmation.
    """
    token = serializers.CharField(required=True)
    uid = serializers.CharField(required=True)
    new_password = serializers.CharField(
        required=True,
        validators=[validate_password]
    )
    new_password_confirm = serializers.CharField(required=True)
    
    def validate(self, attrs):
        """Validate password reset confirmation."""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': 'Password fields do not match.'
            })
        return attrs