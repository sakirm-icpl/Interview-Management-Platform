"""
URL patterns for users app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

app_name = 'users'

router = DefaultRouter()
router.register(r'users', views.UserViewSet, basename='user')
router.register(r'invitations', views.InvitationViewSet, basename='invitation')
router.register(r'profiles', views.UserProfileViewSet, basename='profile')

urlpatterns = [
    # Authentication
    path('login/', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Router URLs
    path('', include(router.urls)),
]