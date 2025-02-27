from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from service.models import Customer, Contact
from django.contrib.auth import get_user_model

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
        
        # Create test client
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

    def test_create_customer_staff(self):
        """Test that staff users can create customers"""
        self.client.force_authenticate(user=self.staff_user)
        payload = {
            'name': 'New Customer',
            'address': '789 New St',
            'city': 'New City',
            'state': 'NS',
            'zip_code': '11111',
            'contacts': [{
                'name': 'New Contact',
                'email': 'new@contact.com',
                'phone': '999-999-9999',
                'is_primary': True
            }]
        }
        res = self.client.post(self.list_url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Customer.objects.count(), 2)
        self.assertEqual(Contact.objects.count(), 2)

    def test_create_customer_regular_user(self):
        """Test that regular users cannot create customers"""
        self.client.force_authenticate(user=self.regular_user)
        payload = {
            'name': 'New Customer',
            'address': '789 New St'
        }
        res = self.client.post(self.list_url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_customers_authenticated(self):
        """Test that authenticated users can list customers"""
        self.client.force_authenticate(user=self.regular_user)
        res = self.client.get(self.list_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(len(res.data['results']) > 0)

    def test_list_customers_unauthenticated(self):
        """Test that unauthenticated users cannot list customers"""
        res = self.client.get(self.list_url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_customer_staff(self):
        """Test that staff users can update customers"""
        self.client.force_authenticate(user=self.staff_user)
        payload = {
            'name': 'Updated Customer',
            'address': '456 New St',
            'city': 'NewCity',
            'state': 'NewState',
            'zip_code': '67890',
            'contacts': [
                {
                    'name': 'Updated Contact',
                    'email': 'updated@example.com',
                    'phone': '222-222-2222',
                    'is_primary': True
                }
            ]
        }
        res = self.client.put(self.detail_url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.name, 'Updated Customer')
        self.assertEqual(self.customer.city, 'NewCity')

    def test_update_customer_regular_user(self):
        """Test that regular users cannot update customers"""
        self.client.force_authenticate(user=self.regular_user)
        payload = {
            'name': 'Updated Customer',
            'address': '456 New St'
        }
        res = self.client.put(self.detail_url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_customer_staff(self):
        """Test that staff users can delete customers"""
        self.client.force_authenticate(user=self.staff_user)
        res = self.client.delete(self.detail_url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Customer.objects.count(), 0)
        self.assertEqual(Contact.objects.count(), 0)

    def test_delete_customer_regular_user(self):
        """Test that regular users cannot delete customers"""
        self.client.force_authenticate(user=self.regular_user)
        res = self.client.delete(self.detail_url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_contact_validation(self):
        """Test contact validation rules"""
        self.client.force_authenticate(user=self.staff_user)
        payload = {
            'name': 'Validation Test Customer',
            'address': '123 Valid St',
            'contacts': [
                {
                    'name': 'Valid Contact',
                    'email': 'invalid-email',  # Invalid email format
                    'phone': '123-456-7890'
                }
            ]
        }
        res = self.client.post(self.list_url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('contacts', res.data)

    def test_multiple_primary_contacts(self):
        """Test handling of multiple primary contacts"""
        self.client.force_authenticate(user=self.staff_user)
        payload = {
            'name': 'Primary Test Customer',
            'address': '123 Primary St',
            'contacts': [
                {
                    'name': 'First Contact',
                    'email': 'first@example.com',
                    'is_primary': True
                },
                {
                    'name': 'Second Contact',
                    'email': 'second@example.com',
                    'is_primary': True
                }
            ]
        }
        res = self.client.post(self.list_url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('contacts', res.data)
