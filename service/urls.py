from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    # Add a basic home view for now
    path('', TemplateView.as_view(template_name='service/home.html'), name='home'),
]
