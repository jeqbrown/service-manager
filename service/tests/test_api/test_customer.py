from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from service.models import Customer, Contact
from datetime import datetime

User = get_user_model()

class CustomerAPITests(TestCase):
    def setUp(self):
        # Create users with different permission levels
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
        
        self.client = APIClient()
        
        # Create test customer
        self.customer = Customer.objects.create(
            name='Test Customer',
            address='123 Test St',
            city='Test City',
            state='TS',
            zip_code='12345',
            created_by=self.staff_user,
            updated_by=self.staff_user
        )
        
        # Create test contact
        self.contact = Contact.objects.create(
            customer=self.customer,
            name='Test Contact',
            email='contact@test.com',
            phone='123-456-7890',
            is_primary=True,
            created_by=self.staff_user,
            updated_by=self.staff_user
        )

        self.list_url = reverse('customer-list')
        self.detail_url = reverse('customer-detail', args=[self.customer.id])

    def test_list_customers_authenticated(self):
        """Test that authenticated users can list customers"""
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_list_customers_unauthenticated(self):
        """Test that unauthenticated users cannot list customers"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_customer_authenticated(self):
        """Test that authenticated users can retrieve a customer"""
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.customer.name)

    def test_create_customer_staff(self):
        """Test that staff users can create customers with nested contacts"""
        self.client.force_authenticate(user=self.staff_user)
        payload = {
            'name': 'New Customer',
            'address': '789 New St',
            'city': 'New City',
            'state': 'NS',
            'zip_code': '54321',
            'contacts': [{
                'name': 'New Contact',
                'email': 'new@contact.com',
                'phone': '999-999-9999',
                'is_primary': True
            }]
        }
        response = self.client.post(self.list_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Customer.objects.count(), 2)
        self.assertEqual(Contact.objects.count(), 2)

    def test_create_customer_regular_user(self):
        """Test that regular users cannot create customers"""
        self.client.force_authenticate(user=self.regular_user)
        payload = {
            'name': 'New Customer',
            'address': '789 New St'
        }
        response = self.client.post(self.list_url, payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_customer_staff(self):
        """Test that staff users can update customers"""
        self.client.force_authenticate(user=self.staff_user)
        payload = {
            'name': 'Updated Customer',
            'address': 'Updated Address'
        }
        response = self.client.patch(self.detail_url, payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.name, 'Updated Customer')

    def test_delete_customer_admin(self):
        """Test that admin users can delete customers"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Customer.objects.count(), 0)

    def test_delete_customer_staff(self):
        """Test that staff users cannot delete customers"""
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_filter_customers(self):
        """Test filtering customers by name and city"""
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(f"{self.list_url}?name=Test")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_search_customers(self):
        """Test searching customers"""
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(f"{self.list_url}?search=Test")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_customer_pagination(self):
        """Test customer list pagination"""
        # Create 11 more customers (12 total)
        for i in range(11):
            Customer.objects.create(
                name=f'Customer {i}',
                address=f'Address {i}',
                city='Test City',
                state='TS',
                zip_code='12345',
                created_by=self.staff_user,
                updated_by=self.staff_user
            )
        
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 10)  # Default page size
        self.assertIsNotNone(response.data['next'])
        self.assertIsNone(response.data['previous'])

    def test_tracking_fields(self):
        """Test that tracking fields are properly set"""
        self.client.force_authenticate(user=self.staff_user)
        payload = {
            'name': 'New Customer',
            'address': '789 New St',
            'city': 'New City',
            'state': 'NS',
            'zip_code': '54321'
        }
        response = self.client.post(self.list_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        new_customer = Customer.objects.get(name='New Customer')
        self.assertEqual(new_customer.created_by, self.staff_user)
        self.assertEqual(new_customer.updated_by, self.staff_user)
