from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()

class AuthAPITests(TestCase):
    """Test the auth API endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        self.login_url = reverse('login')
        self.me_url = reverse('me')
        
        # Create test user
        self.user = User.objects.create_user(
            username='testuser@example.com',
            email='testuser@example.com',
            password='testpass123'
        )
    
    def test_login_success(self):
        """Test login with valid credentials"""
        payload = {
            'email': 'testuser@example.com',
            'password': 'testpass123'
        }
        res = self.client.post(self.login_url, payload)
        
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('token', res.data)
        self.assertIn('refresh', res.data)
        self.assertIn('user', res.data)
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        payload = {
            'email': 'testuser@example.com',
            'password': 'wrongpass'
        }
        res = self.client.post(self.login_url, payload)
        
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_me_authenticated(self):
        """Test retrieving user profile when authenticated"""
        # Authenticate the client
        self.client.force_authenticate(user=self.user)
        res = self.client.get(self.me_url)
        
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['email'], self.user.email)
    
    def test_me_unauthenticated(self):
        """Test retrieving user profile when unauthenticated"""
        res = self.client.get(self.me_url)
        
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)