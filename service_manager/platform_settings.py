import os
import dj_database_url
from .settings import *

# Debug should be False in production
DEBUG = False

# Ensure ALLOWED_HOSTS is properly set
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')
if os.getenv('APP_DOMAIN'):
    ALLOWED_HOSTS.append(os.getenv('APP_DOMAIN'))
if os.getenv('PUBLIC_URL'):
    ALLOWED_HOSTS.append(os.getenv('PUBLIC_URL'))

# Database configuration
DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv('DATABASE_URL'),
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# If no DATABASE_URL is set, use these default settings
if 'default' not in DATABASES:
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'service_manager_db'),
        'USER': os.getenv('DB_USER', 'service_manager_user'),
        'PASSWORD': os.getenv('DB_PASSWORD', ''),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }

# Security settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# Static files
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

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
