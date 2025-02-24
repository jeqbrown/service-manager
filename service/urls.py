from django.urls import path
from .admin.views import instrument_type_options, get_model_option

urlpatterns = [
    path('admin/service/instrumenttype/ajax/options/', 
         instrument_type_options, 
         name='admin_instrumenttype_options'),
    path('admin/service/<str:model_name>/<int:object_id>/get_option/',
         get_model_option,
         name='admin_get_model_option'),
]
