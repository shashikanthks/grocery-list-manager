from django.db import models
from django.conf import settings
from apps.usergroups.models import UserGroup


class GroceryList(models.Model):
    """
    Represents a grocery list for a user group.
    One list per group.
    """
    group = models.OneToOneField(
        UserGroup,
        on_delete=models.CASCADE,
        related_name='grocery_list'
    )
    name = models.CharField(max_length=100, default='Grocery List')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'grocery_lists'
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.name} ({self.group.name})"


class GroceryItem(models.Model):
    """
    Represents an item in a grocery list.
    """
    
    class Category(models.TextChoices):
        PRODUCE = 'produce', 'Produce'
        DAIRY = 'dairy', 'Dairy'
        MEAT = 'meat', 'Meat & Seafood'
        BAKERY = 'bakery', 'Bakery'
        FROZEN = 'frozen', 'Frozen'
        PANTRY = 'pantry', 'Pantry'
        BEVERAGES = 'beverages', 'Beverages'
        SNACKS = 'snacks', 'Snacks'
        HOUSEHOLD = 'household', 'Household'
        PERSONAL = 'personal', 'Personal Care'
        OTHER = 'other', 'Other'

    grocery_list = models.ForeignKey(
        GroceryList,
        on_delete=models.CASCADE,
        related_name='items'
    )
    name = models.CharField(max_length=200)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        default=Category.OTHER
    )
    notes = models.TextField(blank=True, default='')
    is_purchased = models.BooleanField(default=False)
    purchased_at = models.DateTimeField(null=True, blank=True)
    purchased_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='purchased_items'
    )
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='added_items'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'grocery_items'
        ordering = ['is_purchased', '-created_at']

    def __str__(self):
        status = '✓' if self.is_purchased else '○'
        return f"{status} {self.name} ({self.quantity})"