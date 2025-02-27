from rest_framework import viewsets, permissions
from django.contrib.auth.models import User
from service.api.serializers import UserSerializer
from service.api.permissions import IsAdminOrSelf

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSelf]
    search_fields = ['username', 'first_name', 'last_name', 'email']