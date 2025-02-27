from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from service.models import Customer, Contact
from datetime import datetime, timedelta

User = get_user_model()

class CustomerAPITests(TestCase):
    def setUp(self):
        # Create test users with different permission levels
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        self.staff_user = User.objects.create_user(
            username='staff',
            email='staff@example.com',
            password='staffpass123',
            is_staff=True
        )
        self.regular_user = User.objects.create_user(
            username='regular',
            email='regular@example.com',
            password='userpass123'
        )
        
        # Create test client
        self.client = APIClient()
        
        # Create some test customers
        self.customer1 = Customer.objects.create(
            name='Test Customer 1',
            address='123 Test St',
            city='Test City',
            state='TS',
            zip_code='12345',
            website='http://test1.com',
            created_by=self.staff_user,
            updated_by=self.staff_user
        )
        
        self.customer2 = Customer.objects.create(
            name='Test Customer 2',
            address='456 Test Ave',
            city='Other City',
            state='TS',
            zip_code='67890',
            website='http://test2.com',
            created_by=self.staff_user,
            updated_by=self.staff_user
        )

        # Create test contact
        self.contact1 = Contact.objects.create(
            customer=self.customer1,
            name='Test Contact',
            email='contact@test.com',
            phone='123-456-7890',
            created_by=self.staff_user,
            updated_by=self.staff_user
        )

        self.list_url = reverse('customer-list')
        self.detail_url = reverse('customer-detail', args=[self.customer1.id])

    def test_list_customers_authenticated(self):
        """Test that authenticated users can list customers"""
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_list_customers_unauthenticated(self):
        """Test that unauthenticated users cannot list customers"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_customer_staff(self):
        """Test that staff users can create customers"""
        self.client.force_authenticate(user=self.staff_user)
        data = {
            'name': 'New Customer',
            'address': '789 New St',
            'city': 'New City',
            'state': 'NS',
            'zip_code': '11111',
            'website': 'http://new.com',
            'contacts': [{
                'name': 'New Contact',
                'email': 'new@contact.com',
                'phone': '999-999-9999'
            }]
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Customer.objects.count(), 3)
        self.assertEqual(response.data['created_by'], self.staff_user.id)

    def test_create_customer_regular_user(self):
        """Test that regular users cannot create customers"""
        self.client.force_authenticate(user=self.regular_user)
        data = {
            'name': 'New Customer',
            'address': '789 New St',
            'city': 'New City',
            'state': 'NS',
            'zip_code': '11111'
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # More tests to be added...