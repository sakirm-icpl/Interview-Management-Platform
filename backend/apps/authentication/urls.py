"""
URL patterns for authentication app.
"""

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

app_name = 'authentication'

urlpatterns = [
    # Authentication endpoints
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('login/', views.CustomTokenObtainPairView.as_view(), name='login'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('status/', views.auth_status, name='auth_status'),
    
    # Password management
    path('change-password/', views.PasswordChangeView.as_view(), name='change_password'),
    path('reset-password/', views.PasswordResetRequestView.as_view(), name='reset_password'),
    path('reset-password/confirm/', views.PasswordResetConfirmView.as_view(), name='reset_password_confirm'),
    
    # User profile endpoints
    path('profile/', views.UserProfileView.as_view(), name='user_profile'),
    path('profile/update/', views.UserUpdateView.as_view(), name='user_update'),
    path('profile/detail/', views.UserProfileDetailView.as_view(), name='user_profile_detail'),
    path('profile/stats/', views.user_stats, name='user_stats'),
    
    # Skills endpoints
    path('skills/', views.SkillListView.as_view(), name='skills_list'),
    path('skills/user/', views.UserSkillListCreateView.as_view(), name='user_skills'),
    path('skills/user/<int:pk>/', views.UserSkillDetailView.as_view(), name='user_skill_detail'),
]