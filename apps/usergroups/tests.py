from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from .models import UserGroup, GroupMembership
from apps.users.models import User


class UserGroupModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_create_group(self):
        """Test creating a User group."""
        group = UserGroup.objects.create(
            name='Test Family',
            description='A test User Group',
            created_by=self.user
        )
        self.assertEqual(group.name, 'Test Family')
        self.assertEqual(group.description, 'A test User Group')
        self.assertEqual(group.created_by, self.user) 


class GroupMembershipModelTests(TestCase):

    def setUp(self):
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='pass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='pass123'
        )
        self.group = UserGroup.objects.create(
            name='Test Family',
            created_by=self.user1
        )

    def test_create_membership(self):
        """Test creating a group membership."""
        membership = GroupMembership.objects.create(
            user=self.user1,
            group=self.group
        )
        self.assertEqual(membership.user, self.user1)
        self.assertEqual(membership.group, self.group)
        self.assertIsNotNone(membership.joined_at)

    def test_membership_uniqueness(self):
        """Test that user can only be in a group once."""
        GroupMembership.objects.create(user=self.user1, group=self.group)
        with self.assertRaises(Exception):
            GroupMembership.objects.create(user=self.user1, group=self.group)


class UserGroupAPITests(APITestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123'
        )
        self.client = APIClient()

    def test_create_group(self):
        """Test creating a new group."""
        self.client.force_authenticate(user=self.user)
        url = reverse('group-list')
        data = {
            'name': 'My Family',
            'description': 'Our User'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'My Family')
        
        # Check that creator is automatically added as member
        group = UserGroup.objects.get(id=response.data['id'])
        self.assertIn(self.user, group.members.all())
        self.assertEqual(group.created_by, self.user)

    def test_delete_group(self):
        """Test deleting a group."""
        group = UserGroup.objects.create(name='To Delete', created_by=self.user)
        GroupMembership.objects.create(user=self.user, group=group)
        
        self.client.force_authenticate(user=self.user)
        url = reverse('group-detail', kwargs={'pk': group.pk})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(UserGroup.objects.filter(id=group.id).exists())