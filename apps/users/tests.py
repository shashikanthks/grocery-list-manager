from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from .models import User


class UserModelTests(TestCase):

    def test_create_user(self):
        """Test creating a user with email and username."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('testpass123'))
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        """Test creating a superuser."""
        admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        self.assertTrue(admin.is_superuser)

class UserAPITests(APITestCase):
    """Tests for User API endpoints."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123'
        )
        self.client = APIClient()

    def test_user_list_requires_authentication(self):
        """Test that user list requires authentication."""
        url = reverse('user-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_list_authenticated(self):
        """Test getting user list when authenticated."""
        self.client.force_authenticate(user=self.user)
        url = reverse('user-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    """Tests for User serializers."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )

    def test_user_serializer_fields(self):
        """Test that UserSerializer includes correct fields."""
        from .serializers import UserSerializer
        serializer = UserSerializer(self.user)
        data = serializer.data
        
        self.assertIn('id', data)
        self.assertIn('username', data)
        self.assertIn('email', data)
        self.assertIn('first_name', data)
        self.assertIn('last_name', data)
        self.assertIn('created_at', data)
        # Password should not be in serialized data
        self.assertNotIn('password', data)

    def test_user_minimal_serializer(self):
        """Test UserMinimalSerializer has limited fields."""
        from .serializers import UserMinimalSerializer
        serializer = UserMinimalSerializer(self.user)
        data = serializer.data
        
        self.assertIn('id', data)
        self.assertIn('username', data)
        self.assertIn('email', data)
        self.assertNotIn('created_at', data)