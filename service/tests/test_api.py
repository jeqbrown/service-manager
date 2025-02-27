from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from ..models import WorkOrder, Customer
from datetime import datetime, timedelta

@override_settings(REST_FRAMEWORK={
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ]
})
class DashboardAPITests(TestCase):
    def setUp(self):
        # Create test user
        User = get_user_model()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Create test client
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # Create test data
        self.customer = Customer.objects.create(
            name='Test Customer',
            email='test@example.com'
        )
        
        # Create some work orders
        self.work_orders = []
        statuses = ['pending', 'completed', 'in_progress']
        for i in range(5):
            wo = WorkOrder.objects.create(
                title=f'Test Work Order {i}',
                customer=self.customer,
                status=statuses[i % 3],
                created_at=timezone.now() - timedelta(days=i),
                scheduled_date=timezone.now() + timedelta(days=i)
            )
            self.work_orders.append(wo)

    def test_dashboard_endpoint_unauthorized(self):
        """Test that unauthorized users cannot access the dashboard"""
        self.client.logout()
        response = self.client.get(reverse('service:dashboard'))
        self.assertEqual(response.status_code, 401)

    def test_dashboard_endpoint_authorized(self):
        """Test that authorized users can access the dashboard"""
        response = self.client.get(reverse('service:dashboard'))
        self.assertEqual(response.status_code, 200)
        
        # Check response structure
        self.assertIn('statistics', response.data)
        self.assertIn('recentWorkOrders', response.data)
        self.assertIn('upcomingServices', response.data)

    def test_dashboard_statistics(self):
        """Test that statistics are calculated correctly"""
        response = self.client.get(reverse('service:dashboard'))
        stats = response.data['statistics']
        
        self.assertEqual(stats['totalWorkOrders'], 5)
        self.assertEqual(
            stats['pendingServices'],
            WorkOrder.objects.filter(status='pending').count()
        )
        self.assertEqual(
            stats['activeCustomers'],
            Customer.objects.filter(workorder__isnull=False).distinct().count()
        )

    def test_dashboard_date_filtering(self):
        """Test that date filtering works correctly"""
        start_date = (timezone.now() - timedelta(days=2)).strftime('%Y-%m-%d')
        end_date = timezone.now().strftime('%Y-%m-%d')
        
        response = self.client.get(
            reverse('service:dashboard'),
            {'startDate': start_date, 'endDate': end_date}
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['recentWorkOrders']), 3)

    def test_invalid_date_format(self):
        """Test handling of invalid date formats"""
        response = self.client.get(
            reverse('service:dashboard'),
            {'startDate': 'invalid-date'}
        )
        self.assertEqual(response.status_code, 400)
