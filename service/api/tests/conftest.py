import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def staff_user():
    return User.objects.create_user(
        username='staff_test',
        password='testpass123',
        is_staff=True
    )

@pytest.fixture
def normal_user():
    return User.objects.create_user(
        username='normal_test',
        password='testpass123'
    )