from django.urls import path
from .views import workorder_views

app_name = 'service'

urlpatterns = [
    path('workorders/', 
         workorder_views.WorkOrderListView.as_view(), 
         name='workorder-list'),
    
    path('workorders/<int:pk>/', 
         workorder_views.WorkOrderDetailView.as_view(), 
         name='workorder-detail'),
]