from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from .models import GroceryList, GroceryItem
from apps.usergroups.models import UserGroup, GroupMembership
from apps.users.models import User


class GroceryListModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.group = UserGroup.objects.create(
            name='Test Family',
            created_by=self.user
        )

    def test_create_grocery_list(self):
        """Test creating a grocery list."""
        grocery_list = GroceryList.objects.create(
            group=self.group,
            name='Weekly Groceries'
        )
        self.assertEqual(grocery_list.name, 'Weekly Groceries')
        self.assertEqual(grocery_list.group, self.group)

    def test_cascade_delete_on_group(self):
        """Test that grocery list is deleted when group is deleted."""
        grocery_list = GroceryList.objects.create(group=self.group)
        list_id = grocery_list.id
        
        self.group.delete()
        self.assertFalse(GroceryList.objects.filter(id=list_id).exists())


class GroceryItemModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.group = UserGroup.objects.create(
            name='Test Family',
            created_by=self.user
        )
        self.grocery_list = GroceryList.objects.create(
            group=self.group,
            name='Weekly Groceries'
        )

    def test_create_grocery_item(self):
        """Test creating a grocery item."""
        item = GroceryItem.objects.create(
            grocery_list=self.grocery_list,
            name='Milk',
            quantity=2,
            category='dairy',
            notes='2% preferred',
            added_by=self.user
        )
        self.assertEqual(item.name, 'Milk')
        self.assertEqual(item.quantity, 2)
        self.assertEqual(item.category, 'dairy')
        self.assertEqual(item.notes, '2% preferred')
        self.assertFalse(item.is_purchased)

    def test_cascade_delete_on_grocery_list(self):
        """Test that items are deleted when grocery list is deleted."""
        item = GroceryItem.objects.create(
            grocery_list=self.grocery_list,
            name='Milk'
        )
        item_id = item.id
        
        self.grocery_list.delete()
        self.assertFalse(GroceryItem.objects.filter(id=item_id).exists())

class GroceryListAPITests(APITestCase):

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
        self.group = UserGroup.objects.create(
            name='Test Family',
            created_by=self.user
        )
        GroupMembership.objects.create(user=self.user, group=self.group)
        self.client = APIClient()

    def test_list_grocery_lists(self):
        """Test listing grocery lists."""
        GroceryList.objects.create(group=self.group, name='My List')
        
        self.client.force_authenticate(user=self.user)
        url = reverse('grocerylist-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_retrieve_list_with_items(self):
        """Test retrieving a list includes items separated by status."""
        grocery_list = GroceryList.objects.create(group=self.group)
        GroceryItem.objects.create(grocery_list=grocery_list, name='Active Item 1')
        GroceryItem.objects.create(grocery_list=grocery_list, name='Active Item 2')
        GroceryItem.objects.create(
            grocery_list=grocery_list,
            name='Purchased Item',
            is_purchased=True,
            purchased_at=timezone.now()
        )
        
        self.client.force_authenticate(user=self.user)
        url = reverse('grocerylist-detail', kwargs={'pk': grocery_list.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['active_items']), 2)
        self.assertEqual(len(response.data['purchased_items']), 1)

    def test_clear_purchased_items(self):
        """Test deleting all purchased items."""
        grocery_list = GroceryList.objects.create(group=self.group)
        GroceryItem.objects.create(grocery_list=grocery_list, name='Active')
        GroceryItem.objects.create(grocery_list=grocery_list, name='Purchased 1', is_purchased=True)
        GroceryItem.objects.create(grocery_list=grocery_list, name='Purchased 2', is_purchased=True)
        
        self.client.force_authenticate(user=self.user)
        url = reverse('grocerylist-clear-purchased', kwargs={'pk': grocery_list.pk})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['deleted_count'], 2)
        self.assertEqual(grocery_list.items.count(), 1)
        self.assertEqual(grocery_list.items.first().name, 'Active')

    def test_grocery_list_requires_authentication(self):
        """Test that grocery list endpoints require authentication."""
        url = reverse('grocerylist-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class GroceryItemAPITests(APITestCase):

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
        self.group = UserGroup.objects.create(
            name='Test Family',
            created_by=self.user
        )
        GroupMembership.objects.create(user=self.user, group=self.group)
        self.grocery_list = GroceryList.objects.create(group=self.group)
        self.client = APIClient()

    def test_create_item(self):
        """Test creating a grocery item."""
        self.client.force_authenticate(user=self.user)
        url = reverse('groceryitem-list')
        data = {
            'grocery_list_id': self.grocery_list.id,
            'name': 'Milk',
            'quantity': 2,
            'category': 'dairy',
            'notes': '2% preferred'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Milk')
        self.assertEqual(response.data['added_by']['username'], 'testuser')

    def test_list_items_with_filters(self):
        """Test listing items with various filters."""
        GroceryItem.objects.create(
            grocery_list=self.grocery_list,
            name='Milk',
            category='dairy'
        )
        GroceryItem.objects.create(
            grocery_list=self.grocery_list,
            name='Apples',
            category='produce'
        )
        GroceryItem.objects.create(
            grocery_list=self.grocery_list,
            name='Cheese',
            category='dairy',
            is_purchased=True
        )
        
        self.client.force_authenticate(user=self.user)
        base_url = reverse('groceryitem-list')
        
        # Filter by list
        response = self.client.get(f'{base_url}?list_id={self.grocery_list.id}')
        self.assertEqual(len(response.data['results']), 3)
        
        # Filter by category
        response = self.client.get(f'{base_url}?category=dairy')
        self.assertEqual(len(response.data['results']), 2)
        
        # Filter by purchase status
        response = self.client.get(f'{base_url}?is_purchased=false')
        self.assertEqual(len(response.data['results']), 2)
        
        # Search by name
        response = self.client.get(f'{base_url}?search=milk')
        self.assertEqual(len(response.data['results']), 1)

    def test_update_item_marks_purchased(self):
        """Test that updating is_purchased sets purchased_at and purchased_by."""
        item = GroceryItem.objects.create(
            grocery_list=self.grocery_list,
            name='Milk'
        )
        
        self.client.force_authenticate(user=self.user)
        url = reverse('groceryitem-detail', kwargs={'pk': item.pk})
        response = self.client.patch(url, {'is_purchased': True})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        item.refresh_from_db()
        self.assertTrue(item.is_purchased)
        self.assertIsNotNone(item.purchased_at)
        self.assertEqual(item.purchased_by, self.user)

    def test_delete_item(self):
        """Test deleting a grocery item."""
        item = GroceryItem.objects.create(
            grocery_list=self.grocery_list,
            name='Milk'
        )
        
        self.client.force_authenticate(user=self.user)
        url = reverse('groceryitem-detail', kwargs={'pk': item.pk})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(GroceryItem.objects.filter(id=item.id).exists())