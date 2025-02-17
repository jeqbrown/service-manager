import os
import dj_database_url
from .settings import *

# Debug should be False in production
DEBUG = False

# Ensure ALLOWED_HOSTS is properly set
ALLOWED_HOSTS = [
    'web-production-d9ef.up.railway.app',
    '.railway.app',
    'localhost',
    '127.0.0.1',
]

# Database configuration
DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv('DATABASE_URL'),
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# Static files configuration
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Security settings
SECURE_SSL_REDIRECT = False  # Set to True if you have SSL configured
SESSION_COOKIE_SECURE = False  # Set to True if you have SSL configured
CSRF_COOKIE_SECURE = False  # Set to True if you have SSL configured
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# Installed apps
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'service',
]
