from django.urls import path
from .api.views import dashboard_view

app_name = 'service'

urlpatterns = [
    path('api/dashboard/', dashboard_view, name='dashboard'),
]
