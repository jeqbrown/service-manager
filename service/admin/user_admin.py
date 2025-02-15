from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model
from django.utils.html import format_html

User = get_user_model()

class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_active', 'group_list')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)

    def group_list(self, obj):
        """Display comma-separated list of group names with color badges"""
        groups = obj.groups.all().order_by('name')
        if not groups:
            return format_html('<span style="color: #999;">No groups</span>')
        
        return format_html(
            ''.join([
                f'<span style="background-color: #447e9b; color: white; padding: 2px 6px; '
                f'border-radius: 3px; margin-right: 4px;">{group.name}</span>'
                for group in groups
            ])
        )
    group_list.short_description = 'Groups'
    group_list.allow_tags = True

    # Preserve the existing fieldsets from UserAdmin
    fieldsets = BaseUserAdmin.fieldsets
    add_fieldsets = BaseUserAdmin.add_fieldsets
