"""
Serializers for user management and authentication.
"""
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User, UserProfile, UserActivity, Invitation


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom token serializer with additional user data."""
    
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Add custom claims
        data['user'] = {
            'id': str(self.user.id),
            'email': self.user.email,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'role': self.user.role,
            'is_verified': self.user.is_verified,
        }
        
        return data


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'email', 'username', 'first_name', 'last_name', 'password', 
            'password_confirm', 'phone_number', 'role'
        ]
        extra_kwargs = {
            'email': {'required': True},
            'username': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile."""
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    skills = serializers.SlugRelatedField(
        many=True, 
        slug_field='name', 
        queryset=UserProfile.objects.none(),
        required=False
    )
    
    class Meta:
        model = UserProfile
        fields = '__all__'
        read_only_fields = ['user']


class UserSerializer(serializers.ModelSerializer):
    """Main user serializer."""
    profile = UserProfileSerializer(read_only=True)
    full_name = serializers.SerializerMethodField()
    role_display = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name', 'full_name',
            'role', 'role_display', 'phone_number', 'profile_picture', 'bio',
            'department', 'job_title', 'experience_years', 'is_verified',
            'is_active', 'created_at', 'updated_at', 'profile'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_verified']
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    
    def get_role_display(self, obj):
        return obj.get_role_display_name()


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user information."""
    
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'phone_number', 'profile_picture',
            'bio', 'address', 'city', 'state', 'country', 'postal_code',
            'department', 'job_title', 'experience_years', 'education',
            'certifications'
        ]


class PasswordChangeSerializer(serializers.Serializer):
    """Serializer for password change."""
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(required=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("New passwords don't match")
        return attrs
    
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect")
        return value


class PasswordResetRequestSerializer(serializers.Serializer):
    """Serializer for password reset request."""
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Serializer for password reset confirmation."""
    token = serializers.CharField()
    new_password = serializers.CharField(validators=[validate_password])
    new_password_confirm = serializers.CharField()
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs


class EmailVerificationSerializer(serializers.Serializer):
    """Serializer for email verification."""
    token = serializers.CharField()


class UserActivitySerializer(serializers.ModelSerializer):
    """Serializer for user activity tracking."""
    
    class Meta:
        model = UserActivity
        fields = '__all__'
        read_only_fields = ['user', 'ip_address', 'user_agent']


class InvitationSerializer(serializers.ModelSerializer):
    """Serializer for user invitations."""
    invited_by = UserSerializer(read_only=True)
    
    class Meta:
        model = Invitation
        fields = '__all__'
        read_only_fields = ['invited_by', 'token', 'is_accepted', 'accepted_at']


class InvitationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating invitations."""
    
    class Meta:
        model = Invitation
        fields = ['email', 'role', 'message', 'expires_at']
    
    def create(self, validated_data):
        validated_data['invited_by'] = self.context['request'].user
        return super().create(validated_data)


class LoginSerializer(serializers.Serializer):
    """Serializer for user login."""
    email = serializers.EmailField()
    password = serializers.CharField()
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            user = authenticate(username=email, password=password)
            if not user:
                raise serializers.ValidationError('Invalid credentials')
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled')
            attrs['user'] = user
        else:
            raise serializers.ValidationError('Must include email and password')
        
        return attrs


class UserListSerializer(serializers.ModelSerializer):
    """Serializer for user list views."""
    full_name = serializers.SerializerMethodField()
    department_name = serializers.CharField(source='department.name', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'full_name', 'role', 'department_name',
            'job_title', 'is_verified', 'is_active', 'created_at'
        ]
    
    def get_full_name(self, obj):
        return obj.get_full_name()