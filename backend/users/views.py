"""
Views for user management and authentication.
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import transaction
from django.core.mail import send_mail
from django.conf import settings
import uuid
import logging

from .models import User, UserProfile, UserActivity, Invitation
from .serializers import (
    CustomTokenObtainPairSerializer, UserRegistrationSerializer, UserSerializer,
    UserUpdateSerializer, PasswordChangeSerializer, PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer, EmailVerificationSerializer, UserActivitySerializer,
    InvitationSerializer, InvitationCreateSerializer, LoginSerializer, UserListSerializer
)

logger = logging.getLogger(__name__)


class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom token view with additional user data."""
    serializer_class = CustomTokenObtainPairSerializer


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet for user management."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter queryset based on user role."""
        user = self.request.user
        if user.is_hr_or_admin():
            return User.objects.all()
        return User.objects.filter(id=user.id)
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            return UserListSerializer
        elif self.action == 'update' or self.action == 'partial_update':
            return UserUpdateSerializer
        return UserSerializer
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user profile."""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def register(self, request):
        """Register a new user."""
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Create user profile
            UserProfile.objects.create(user=user)
            # Send verification email
            self._send_verification_email(user)
            return Response({
                'message': 'User registered successfully. Please check your email for verification.',
                'user_id': str(user.id)
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def verify_email(self, request):
        """Verify user email."""
        serializer = EmailVerificationSerializer(data=request.data)
        if serializer.is_valid():
            token = serializer.validated_data['token']
            try:
                user = User.objects.get(email_verification_token=token)
                if user.email_verification_expires and user.email_verification_expires > timezone.now():
                    user.is_verified = True
                    user.email_verification_token = None
                    user.email_verification_expires = None
                    user.save()
                    return Response({'message': 'Email verified successfully'})
                else:
                    return Response({'error': 'Verification token expired'}, status=status.HTTP_400_BAD_REQUEST)
            except User.DoesNotExist:
                return Response({'error': 'Invalid verification token'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def change_password(self, request):
        """Change user password."""
        serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({'message': 'Password changed successfully'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def request_password_reset(self, request):
        """Request password reset."""
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = User.objects.get(email=email)
                token = uuid.uuid4()
                user.password_reset_token = token
                user.password_reset_expires = timezone.now() + timezone.timedelta(hours=24)
                user.save()
                self._send_password_reset_email(user, token)
                return Response({'message': 'Password reset email sent'})
            except User.DoesNotExist:
                return Response({'message': 'Password reset email sent'})  # Don't reveal if user exists
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def reset_password(self, request):
        """Reset password with token."""
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            token = serializer.validated_data['token']
            try:
                user = User.objects.get(password_reset_token=token)
                if user.password_reset_expires and user.password_reset_expires > timezone.now():
                    user.set_password(serializer.validated_data['new_password'])
                    user.password_reset_token = None
                    user.password_reset_expires = None
                    user.save()
                    return Response({'message': 'Password reset successfully'})
                else:
                    return Response({'error': 'Reset token expired'}, status=status.HTTP_400_BAD_REQUEST)
            except User.DoesNotExist:
                return Response({'error': 'Invalid reset token'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def activities(self, request):
        """Get user activities."""
        activities = UserActivity.objects.filter(user=request.user)
        serializer = UserActivitySerializer(activities, many=True)
        return Response(serializer.data)
    
    def _send_verification_email(self, user):
        """Send email verification."""
        try:
            token = uuid.uuid4()
            user.email_verification_token = token
            user.email_verification_expires = timezone.now() + timezone.timedelta(hours=24)
            user.save()
            
            verification_url = f"{settings.FRONTEND_URL}/verify-email?token={token}"
            send_mail(
                'Verify Your Email',
                f'Please click the following link to verify your email: {verification_url}',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
        except Exception as e:
            logger.error(f"Failed to send verification email: {e}")
    
    def _send_password_reset_email(self, user, token):
        """Send password reset email."""
        try:
            reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"
            send_mail(
                'Reset Your Password',
                f'Please click the following link to reset your password: {reset_url}',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
        except Exception as e:
            logger.error(f"Failed to send password reset email: {e}")


class InvitationViewSet(viewsets.ModelViewSet):
    """ViewSet for user invitations."""
    queryset = Invitation.objects.all()
    serializer_class = InvitationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter queryset based on user role."""
        user = self.request.user
        if user.is_hr_or_admin():
            return Invitation.objects.all()
        return Invitation.objects.filter(email=user.email)
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'create':
            return InvitationCreateSerializer
        return InvitationSerializer
    
    def perform_create(self, serializer):
        """Create invitation and send email."""
        invitation = serializer.save()
        self._send_invitation_email(invitation)
    
    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        """Accept invitation."""
        invitation = self.get_object()
        if invitation.is_expired():
            return Response({'error': 'Invitation has expired'}, status=status.HTTP_400_BAD_REQUEST)
        
        if invitation.is_accepted:
            return Response({'error': 'Invitation already accepted'}, status=status.HTTP_400_BAD_REQUEST)
        
        invitation.accept(request.user)
        return Response({'message': 'Invitation accepted successfully'})
    
    def _send_invitation_email(self, invitation):
        """Send invitation email."""
        try:
            invitation_url = f"{settings.FRONTEND_URL}/accept-invitation?token={invitation.token}"
            send_mail(
                f'You are invited to join {settings.SITE_NAME}',
                f'You have been invited to join as {invitation.get_role_display()}. '
                f'Click here to accept: {invitation_url}',
                settings.DEFAULT_FROM_EMAIL,
                [invitation.email],
                fail_silently=False,
            )
        except Exception as e:
            logger.error(f"Failed to send invitation email: {e}")


class UserProfileViewSet(viewsets.ModelViewSet):
    """ViewSet for user profile management."""
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter queryset based on user."""
        return UserProfile.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Create profile for current user."""
        serializer.save(user=self.request.user)