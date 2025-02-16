from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

class UserAdmin(BaseUserAdmin):
    search_fields = ['username', 'first_name', 'last_name', 'email']
    ordering = ['username']
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff']
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'groups']

# Register the User model with the custom admin site
admin_site.register(User, UserAdmin)
