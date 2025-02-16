def get_status_badge(status):
    status_colors = {
        'open': '#ffc107',      # yellow
        'in_progress': '#17a2b8',  # blue
        'completed': '#28a745',    # green
        'cancelled': '#dc3545',    # red
        'approved': '#28a745',     # green
        'pending': '#ffc107',      # yellow
        'rejected': '#dc3545',     # red
    }
    
    status_lower = status.lower() if isinstance(status, str) else ''
    color = status_colors.get(status_lower, '#6c757d')  # default gray
    
    return format_html(
        '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
        color,
        status
    )