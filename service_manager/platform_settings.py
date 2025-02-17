import os
from .settings import *

# Debug should be False in production
DEBUG = os.getenv('DEBUG', 'False') == 'True'

# Get allowed hosts from environment and split into list
allowed_hosts_env = os.getenv('ALLOWED_HOST', '').split(',')

# Allow DigitalOcean App Platform URLs and custom domain
ALLOWED_HOSTS = [
    'stingray-app-rjzyb.ondigitalocean.app',
    'svcflo.com',
    'www.svcflo.com',
] + allowed_hosts_env

# Print environment variables for debugging (will show in DigitalOcean logs)
print("Database Environment Variables:")
print(f"POSTGRES_DB: {os.getenv('POSTGRES_DB', 'NOT SET')}")
print(f"POSTGRES_USER: {os.getenv('POSTGRES_USER', 'NOT SET')}")
print(f"POSTGRES_HOST: {os.getenv('POSTGRES_HOST', 'NOT SET')}")
print(f"POSTGRES_PORT: {os.getenv('POSTGRES_PORT', 'NOT SET')}")

# Configure database with fallback values
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB'),
        'USER': os.getenv('POSTGRES_USER'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD'),
        'HOST': os.getenv('POSTGRES_HOST'),
        'PORT': os.getenv('POSTGRES_PORT', '5432'),
    }
}

# Verify database configuration
if not all([DATABASES['default']['NAME'],
           DATABASES['default']['USER'],
           DATABASES['default']['PASSWORD'],
           DATABASES['default']['HOST']]):
    raise ImproperlyConfigured(
        "Database configuration is incomplete. Please check your environment variables: "
        "POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST"
    )

# Static files configuration
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'

# Security settings for production
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# Add whitenoise middleware for static files
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
