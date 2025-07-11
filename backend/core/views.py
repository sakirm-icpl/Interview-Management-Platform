"""
Core views for Interview Management Platform.
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """Health check endpoint for monitoring."""
    return Response({
        'status': 'healthy',
        'message': 'Interview Management Platform is running',
        'timestamp': '2024-01-01T00:00:00Z'
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def api_info(request):
    """API information endpoint."""
    return Response({
        'name': 'Interview Management Platform API',
        'version': '1.0.0',
        'description': 'Complete API for AI-powered interview management system',
        'endpoints': {
            'authentication': '/api/auth/',
            'users': '/api/v1/users/',
            'jobs': '/api/v1/jobs/',
            'interviews': '/api/v1/interviews/',
            'chatbot': '/api/v1/chatbot/',
            'offers': '/api/v1/offers/',
            'analytics': '/api/v1/analytics/',
            'documentation': '/api/docs/',
        }
    })


def custom_404(request, exception=None):
    """Custom 404 error handler."""
    return JsonResponse({
        'error': 'Not Found',
        'message': 'The requested resource was not found',
        'status_code': 404
    }, status=404)


def custom_500(request, exception=None):
    """Custom 500 error handler."""
    logger.error(f"Internal server error: {exception}")
    return JsonResponse({
        'error': 'Internal Server Error',
        'message': 'An unexpected error occurred',
        'status_code': 500
    }, status=500)


@api_view(['GET'])
def system_status(request):
    """System status endpoint for monitoring."""
    from django.db import connection
    from django.core.cache import cache
    import psutil
    import os
    
    # Database health check
    db_healthy = False
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            db_healthy = True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
    
    # Cache health check
    cache_healthy = False
    try:
        cache.set('health_check', 'ok', 10)
        cache_healthy = cache.get('health_check') == 'ok'
    except Exception as e:
        logger.error(f"Cache health check failed: {e}")
    
    # System metrics
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
    except ImportError:
        cpu_percent = None
        memory = None
        disk = None
    
    return Response({
        'status': 'operational' if db_healthy and cache_healthy else 'degraded',
        'services': {
            'database': 'healthy' if db_healthy else 'unhealthy',
            'cache': 'healthy' if cache_healthy else 'unhealthy',
        },
        'metrics': {
            'cpu_percent': cpu_percent,
            'memory_percent': memory.percent if memory else None,
            'disk_percent': disk.percent if disk else None,
        },
        'environment': {
            'debug': os.environ.get('DEBUG', 'False'),
            'environment': os.environ.get('ENVIRONMENT', 'development'),
        }
    })