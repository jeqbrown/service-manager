from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Count
from datetime import datetime, timedelta
from ...models import WorkOrder, Customer
from ..serializers import DashboardWorkOrderSerializer, DashboardUpcomingServiceSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_view(request):
    # Get date range filters from request
    start_date = request.GET.get('startDate')
    end_date = request.GET.get('endDate')
    
    # Convert string dates to datetime objects if provided
    try:
        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
    except ValueError:
        return Response({'error': 'Invalid date format'}, status=400)
    
    # Base queryset with date filtering
    base_queryset = WorkOrder.objects.all()
    if start_date:
        base_queryset = base_queryset.filter(created_at__gte=start_date)
    if end_date:
        base_queryset = base_queryset.filter(created_at__lte=end_date)

    # Get statistics
    statistics = {
        'totalWorkOrders': base_queryset.count(),
        'pendingServices': base_queryset.filter(status='pending').count(),
        'activeCustomers': Customer.objects.filter(
            workorder__in=base_queryset
        ).distinct().count(),
    }

    # Get recent work orders
    recent_work_orders = base_queryset.order_by('-created_at')[:5]
    
    # Get upcoming services
    upcoming_services = WorkOrder.objects.filter(
        status='pending',
        scheduled_date__gte=timezone.now()
    ).order_by('scheduled_date')[:5]

    response_data = {
        'statistics': statistics,
        'recentWorkOrders': DashboardWorkOrderSerializer(
            recent_work_orders, 
            many=True
        ).data,
        'upcomingServices': DashboardUpcomingServiceSerializer(
            upcoming_services, 
            many=True
        ).data,
    }

    return Response(response_data)