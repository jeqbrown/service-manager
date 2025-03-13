from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from service.models import Customer, Contact
from datetime import datetime, timedelta
from ..serializers import CustomerSerializer

User = get_user_model()

class CustomerAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        # Create test users
        self.staff_user = User.objects.create_user(
            username='staff_user',
            password='testpass123',
            is_staff=True
        )
        self.normal_user = User.objects.create_user(
            username='normal_user',
            password='testpass123'
        )

        # Create test customer
        self.customer = Customer.objects.create(
            name='Test Company',
            address='123 Test St',
            city='Test City',
            state='TS',
            zip_code='12345',
            website='www.test.com',
            created_by=self.staff_user,
            updated_by=self.staff_user
        )

        self.customer_list_url = reverse('customer-list')
        self.customer_detail_url = reverse('customer-detail', args=[self.customer.id])

    def test_list_customers_authenticated(self):
        """Test that authenticated users can list customers"""
        self.client.force_authenticate(user=self.normal_user)
        response = self.client.get(self.customer_list_url)
        
        customers = Customer.objects.all()
        serializer = CustomerSerializer(customers, many=True)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'], serializer.data)

    def test_list_customers_unauthenticated(self):
        """Test that unauthenticated users cannot list customers"""
        response = self.client.get(self.customer_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_customer_staff(self):
        """Test creating a customer as staff user"""
        self.client.force_authenticate(user=self.staff_user)
        payload = {
            'name': 'New Company',
            'address': '456 New St',
            'city': 'New City',
            'state': 'NS',
            'zip_code': '67890',
            'website': 'www.new.com'
        }
        response = self.client.post(self.customer_list_url, payload)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        customer = Customer.objects.get(id=response.data['id'])
        self.assertEqual(customer.name, payload['name'])
        self.assertEqual(customer.created_by, self.staff_user)

    def test_create_customer_non_staff(self):
        """Test creating a customer as non-staff user fails"""
        self.client.force_authenticate(user=self.normal_user)
        payload = {
            'name': 'New Company',
            'address': '456 New St',
            'city': 'New City',
            'state': 'NS',
            'zip_code': '67890'
        }
        response = self.client.post(self.customer_list_url, payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_filter_customers(self):
        """Test filtering customers"""
        Customer.objects.create(
            name='Another Company',
            city='Different City',
            state='DS',
            created_by=self.staff_user,
            updated_by=self.staff_user
        )
        
        self.client.force_authenticate(user=self.normal_user)
        
        # Test city filter
        response = self.client.get(f'{self.customer_list_url}?city=Test City')
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Test Company')

        # Test name contains filter
        response = self.client.get(f'{self.customer_list_url}?name__contains=Another')
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Another Company')

    def test_search_customers(self):
        """Test searching customers"""
        self.client.force_authenticate(user=self.normal_user)
        response = self.client.get(f'{self.customer_list_url}?search=Test')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Test Company')

    def test_ordering_customers(self):
        """Test ordering customers"""
        Customer.objects.create(
            name='Alpha Company',
            created_by=self.staff_user,
            updated_by=self.staff_user
        )
        
        self.client.force_authenticate(user=self.normal_user)
        
        # Test ordering by name
        response = self.client.get(f'{self.customer_list_url}?ordering=name')
        self.assertEqual(response.data['results'][0]['name'], 'Alpha Company')
        
        # Test reverse ordering
        response = self.client.get(f'{self.customer_list_url}?ordering=-name')
        self.assertEqual(response.data['results'][0]['name'], 'Test Company')

    def test_customer_contacts(self):
        """Test customer contacts endpoint"""
        contact = Contact.objects.create(
            customer=self.customer,
            name='John Doe',
            email='john@test.com',
            phone='1234567890',
            created_by=self.staff_user,
            updated_by=self.staff_user
        )
        
        self.client.force_authenticate(user=self.normal_user)
        response = self.client.get(
            reverse('customer-contacts', args=[self.customer.id])
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'John Doe')

    def test_add_customer_contact(self):
        """Test adding contact to customer"""
        self.client.force_authenticate(user=self.staff_user)
        payload = {
            'name': 'Jane Doe',
            'email': 'jane@test.com',
            'phone': '0987654321'
        }
        
        response = self.client.post(
            reverse('customer-add-contact', args=[self.customer.id]),
            payload
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Contact.objects.count(), 1)
        contact = Contact.objects.first()
        self.assertEqual(contact.name, 'Jane Doe')
        self.assertEqual(contact.customer, self.customer)

    def test_update_customer(self):
        """Test updating a customer"""
        self.client.force_authenticate(user=self.staff_user)
        payload = {
            'name': 'Updated Company',
            'address': 'Updated Address'
        }
        
        response = self.client.patch(self.customer_detail_url, payload)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.name, 'Updated Company')
        self.assertEqual(self.customer.updated_by, self.staff_user)

    def test_delete_customer(self):
        """Test deleting a customer"""
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.delete(self.customer_detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Customer.objects.filter(id=self.customer.id).exists())