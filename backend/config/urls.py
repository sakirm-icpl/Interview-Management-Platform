"""
URL configuration for Interview Management Platform.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Swagger/OpenAPI Schema
schema_view = get_schema_view(
    openapi.Info(
        title="Interview Management Platform API",
        default_version='v1',
        description="Complete API for AI-powered interview management system",
        terms_of_service="https://www.yourapp.com/terms/",
        contact=openapi.Contact(email="contact@yourapp.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # API Documentation
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
    # Authentication
    path('api/auth/', include('rest_framework_simplejwt.urls')),
    path('api/auth/', include('allauth.urls')),
    
    # API Endpoints
    path('api/v1/', include([
        path('users/', include('users.urls')),
        path('jobs/', include('jobs.urls')),
        path('interviews/', include('interviews.urls')),
        path('chatbot/', include('chatbot.urls')),
        path('offers/', include('offers.urls')),
        path('analytics/', include('analytics.urls')),
    ])),
    
    # Health Check
    path('health/', include('core.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Custom error handlers
handler404 = 'core.views.custom_404'
handler500 = 'core.views.custom_500'