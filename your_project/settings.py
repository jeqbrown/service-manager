STATICFILES_DIRS = [
    # ...
]

# Ensure CSS files are loaded in the correct order
ADMIN_CSS_FILES = [
    'admin/css/theme.css',        # Core variables first
    'admin/css/base.css',         # Django admin base styles
    'admin/css/custom_admin.css'  # Your custom overrides last
]