from .settings import *

# Production-specific settings
DEBUG = False

# Update this with your DigitalOcean droplet's IP and domain
ALLOWED_HOSTS = ['your-domain.com', 'your-droplet-ip']

# Security settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Database settings (using PostgreSQL)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'service_manager_db',
        'USER': 'service_manager_user',
        'PASSWORD': '',  # Set this via environment variable
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Static and media files (using DigitalOcean Spaces or similar)
STATIC_ROOT = '/var/www/service_manager/static/'
MEDIA_ROOT = '/var/www/service_manager/media/'