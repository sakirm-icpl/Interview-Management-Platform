"""
Authentication views for the Interview Management Platform.
"""

from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from .models import User, UserProfile, Skill, UserSkill
from .serializers import (
    UserRegistrationSerializer,
    CustomTokenObtainPairSerializer,
    UserSerializer,
    UserUpdateSerializer,
    UserProfileSerializer,
    SkillSerializer,
    UserSkillSerializer,
    PasswordChangeSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
)
from .permissions import IsOwnerOrReadOnly
from apps.notifications.tasks import send_email_notification


class UserRegistrationView(generics.CreateAPIView):
    """
    Register a new user account.
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    @extend_schema(
        summary="Register a new user",
        description="Create a new user account with role-based access",
        tags=["Authentication"]
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            
            # Send welcome email (async task)
            send_email_notification.delay(
                to_email=user.email,
                subject="Welcome to Interview Platform",
                template_name="welcome_email",
                context={
                    'user_name': user.full_name,
                    'role': user.get_role_display()
                }
            )
            
            return Response(
                {
                    'message': 'Account created successfully',
                    'user': UserSerializer(user).data
                },
                status=status.HTTP_201_CREATED
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom JWT token obtain view with additional user data.
    """
    serializer_class = CustomTokenObtainPairSerializer
    
    @extend_schema(
        summary="Obtain JWT token pair",
        description="Login with email and password to get access and refresh tokens",
        tags=["Authentication"]
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    Retrieve and update user profile.
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    @extend_schema(
        summary="Get user profile",
        description="Retrieve the authenticated user's profile information",
        tags=["User Profile"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Update user profile",
        description="Update the authenticated user's profile information",
        tags=["User Profile"]
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)
    
    @extend_schema(
        summary="Partially update user profile",
        description="Partially update the authenticated user's profile information",
        tags=["User Profile"]
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)


class UserUpdateView(generics.UpdateAPIView):
    """
    Update user basic information.
    """
    serializer_class = UserUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    @extend_schema(
        summary="Update user information",
        description="Update user's basic information like name, phone, etc.",
        tags=["User Profile"]
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)


class UserProfileDetailView(generics.RetrieveUpdateAPIView):
    """
    Retrieve and update detailed user profile.
    """
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        profile, created = UserProfile.objects.get_or_create(
            user=self.request.user
        )
        return profile
    
    @extend_schema(
        summary="Get detailed user profile",
        description="Retrieve detailed profile information including skills, experience, etc.",
        tags=["User Profile"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Update detailed user profile",
        description="Update detailed profile information",
        tags=["User Profile"]
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)


class PasswordChangeView(APIView):
    """
    Change user password.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Change password",
        description="Change the authenticated user's password",
        request=PasswordChangeSerializer,
        tags=["Authentication"]
    )
    def post(self, request):
        serializer = PasswordChangeSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            
            # Update session auth hash to keep user logged in
            update_session_auth_hash(request, user)
            
            return Response(
                {'message': 'Password changed successfully'},
                status=status.HTTP_200_OK
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetRequestView(APIView):
    """
    Request password reset via email.
    """
    permission_classes = [permissions.AllowAny]
    
    @extend_schema(
        summary="Request password reset",
        description="Send password reset email to user",
        request=PasswordResetRequestSerializer,
        tags=["Authentication"]
    )
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = User.objects.get(email=email, is_active=True)
            
            # Generate password reset token
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            # Send password reset email (async task)
            send_email_notification.delay(
                to_email=user.email,
                subject="Password Reset Request",
                template_name="password_reset_email",
                context={
                    'user_name': user.full_name,
                    'reset_url': f"{request.build_absolute_uri('/reset-password/')}?token={token}&uid={uid}"
                }
            )
            
            return Response(
                {'message': 'Password reset email sent successfully'},
                status=status.HTTP_200_OK
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmView(APIView):
    """
    Confirm password reset with token.
    """
    permission_classes = [permissions.AllowAny]
    
    @extend_schema(
        summary="Confirm password reset",
        description="Reset password using token from email",
        request=PasswordResetConfirmSerializer,
        tags=["Authentication"]
    )
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                uid = force_str(urlsafe_base64_decode(serializer.validated_data['uid']))
                user = User.objects.get(pk=uid, is_active=True)
                token = serializer.validated_data['token']
                
                if default_token_generator.check_token(user, token):
                    user.set_password(serializer.validated_data['new_password'])
                    user.save()
                    
                    return Response(
                        {'message': 'Password reset successfully'},
                        status=status.HTTP_200_OK
                    )
                else:
                    return Response(
                        {'error': 'Invalid or expired token'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            except (TypeError, ValueError, OverflowError, User.DoesNotExist):
                return Response(
                    {'error': 'Invalid reset link'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SkillListView(generics.ListAPIView):
    """
    List all available skills.
    """
    queryset = Skill.objects.filter(is_active=True)
    serializer_class = SkillSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="List skills",
        description="Get list of all available skills",
        tags=["Skills"],
        parameters=[
            OpenApiParameter(
                name='category',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter by skill category'
            ),
            OpenApiParameter(
                name='search',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Search skills by name'
            ),
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by category
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)
        
        # Search by name
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(name__icontains=search)
        
        return queryset


class UserSkillListCreateView(generics.ListCreateAPIView):
    """
    List and create user skills.
    """
    serializer_class = UserSkillSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return UserSkill.objects.filter(user=self.request.user)
    
    @extend_schema(
        summary="List user skills",
        description="Get list of authenticated user's skills",
        tags=["User Skills"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Add user skill",
        description="Add a new skill to the authenticated user's profile",
        tags=["User Skills"]
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class UserSkillDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a user skill.
    """
    serializer_class = UserSkillSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    
    def get_queryset(self):
        return UserSkill.objects.filter(user=self.request.user)
    
    @extend_schema(
        summary="Get user skill",
        description="Get details of a specific user skill",
        tags=["User Skills"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Update user skill",
        description="Update a specific user skill",
        tags=["User Skills"]
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)
    
    @extend_schema(
        summary="Delete user skill",
        description="Remove a skill from the user's profile",
        tags=["User Skills"]
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


@extend_schema(
    summary="Check authentication status",
    description="Check if the user is authenticated and return user data",
    tags=["Authentication"]
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def auth_status(request):
    """
    Check authentication status and return user data.
    """
    user_data = UserSerializer(request.user).data
    return Response({
        'authenticated': True,
        'user': user_data
    })


@extend_schema(
    summary="Get user statistics",
    description="Get user-related statistics for dashboard",
    tags=["User Profile"]
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_stats(request):
    """
    Get user statistics for dashboard.
    """
    user = request.user
    
    if user.is_candidate:
        # Candidate statistics
        from apps.jobs.models import JobApplication
        from apps.interviews.models import Interview
        
        stats = {
            'applications': JobApplication.objects.filter(candidate=user).count(),
            'interviews': Interview.objects.filter(candidate=user).count(),
            'skills': UserSkill.objects.filter(user=user).count(),
            'profile_completion': calculate_profile_completion(user),
        }
    else:
        # HR/Admin statistics
        from apps.jobs.models import Job, JobApplication
        from apps.interviews.models import Interview
        
        stats = {
            'jobs_posted': Job.objects.filter(created_by=user).count(),
            'total_applications': JobApplication.objects.filter(
                job__created_by=user
            ).count(),
            'interviews_scheduled': Interview.objects.filter(
                job__created_by=user
            ).count(),
            'active_jobs': Job.objects.filter(
                created_by=user,
                is_active=True
            ).count(),
        }
    
    return Response(stats)


def calculate_profile_completion(user):
    """
    Calculate profile completion percentage.
    """
    completion_fields = [
        user.first_name,
        user.last_name,
        user.phone_number,
        user.date_of_birth,
    ]
    
    # Check profile fields
    try:
        profile = user.profile
        completion_fields.extend([
            profile.bio,
            profile.linkedin_url,
            profile.years_of_experience,
            profile.resume,
        ])
    except UserProfile.DoesNotExist:
        pass
    
    # Add skills
    if UserSkill.objects.filter(user=user).exists():
        completion_fields.append(True)
    else:
        completion_fields.append(False)
    
    completed_fields = sum(1 for field in completion_fields if field)
    total_fields = len(completion_fields)
    
    return round((completed_fields / total_fields) * 100, 2) if total_fields > 0 else 0