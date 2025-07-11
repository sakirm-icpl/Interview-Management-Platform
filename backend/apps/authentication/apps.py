"""
Django app configuration for authentication app.
"""

from django.apps import AppConfig


class AuthenticationConfig(AppConfig):
    """
    Configuration for authentication app.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.authentication'
    verbose_name = 'User Authentication'
    
    def ready(self):
        """
        Import signals when the app is ready.
        """
        try:
            import apps.authentication.signals  # noqa F401
        except ImportError:
            pass