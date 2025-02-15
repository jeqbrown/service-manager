from django.contrib import admin
from typing import Optional
from django.utils.html import format_html

def get_status_badge(status: str, display_text: Optional[str] = None) -> str:
    """Generate an HTML status badge with appropriate colors."""
    colors = get_status_colors(status, display_text)
    
    return format_html(
        '<span style="background-color: {}; color: {}; padding: 4px 8px; '
        'border-radius: 4px; font-size: 12px; font-weight: 500;">{}</span>',
        colors['bg_color'],
        colors['text_color'],
        colors['display_text']
    )

def get_status_colors(status: str, display_text: Optional[str] = None) -> dict:
    """Get the colors and display text for a given status."""
    status_key = status.lower().replace(' ', '_')  # Convert "In Progress" to "in_progress"
    
    colors = {
        'draft': {'bg': '#f97316', 'text': '#ffffff'},      # Orange
        'open': {'bg': '#0dcaf0', 'text': '#000000'},       # Info/Cyan
        'pending': {'bg': '#ffc107', 'text': '#000000'},    # Yellow
        'in_progress': {'bg': '#ffc107', 'text': '#000000'},# Yellow
        'completed': {'bg': '#198754', 'text': '#ffffff'},   # Green
        'active': {'bg': '#198754', 'text': '#ffffff'},      # Green
        'expired': {'bg': '#dc3545', 'text': '#ffffff'},     # Red
        'rejected': {'bg': '#dc3545', 'text': '#ffffff'},    # Red
        'approved': {'bg': '#198754', 'text': '#ffffff'},    # Green
    }
    
    status_colors = colors.get(status_key, {'bg': '#6c757d', 'text': '#ffffff'})
    
    return {
        'bg_color': status_colors['bg'],
        'text_color': status_colors['text'],
        'display_text': display_text or status.replace('_', ' ').title()
    }

class ColoredStatusFilter(admin.SimpleListFilter):
    """Base class for colored status filters"""
    
    @property
    def status_choices(self):
        raise NotImplementedError("Subclasses must implement status_choices")

    def lookups(self, request, model_admin):
        return self.status_choices

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(**{self.parameter_name: self.value()})
        return queryset

class ServiceReportStatusFilter(ColoredStatusFilter):
    title = 'Status'
    parameter_name = 'approval_status'

    def lookups(self, request, model_admin):
        return (
            ('pending', 'Pending'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
        )

def register_colored_filter(admin_class, field_name: str) -> None:
    """Register a colored status filter for the given admin class and field."""
    class DynamicColoredFilter(ColoredStatusFilter):
        title = field_name.replace('_', ' ').title()
        parameter_name = field_name
        
        @property
        def status_choices(self):
            return admin_class.model._meta.get_field(field_name).choices

    if isinstance(admin_class.list_filter, tuple):
        admin_class.list_filter = list(admin_class.list_filter)
    
    if field_name in admin_class.list_filter:
        idx = admin_class.list_filter.index(field_name)
        admin_class.list_filter[idx] = DynamicColoredFilter
    else:
        admin_class.list_filter.append(DynamicColoredFilter)
