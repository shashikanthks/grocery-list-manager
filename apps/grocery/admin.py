from django.contrib import admin
from .models import GroceryList, GroceryItem


class GroceryItemInline(admin.TabularInline):
    model = GroceryItem
    extra = 0
    fields = ['name', 'quantity', 'category', 'is_purchased', 'added_by']
    raw_id_fields = ['added_by']


@admin.register(GroceryList)
class GroceryListAdmin(admin.ModelAdmin):
    list_display = ['name', 'group', 'active_items_count', 'purchased_items_count', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['name', 'group__name']
    raw_id_fields = ['group']
    inlines = [GroceryItemInline]
    
    def active_items_count(self, obj):
        return obj.items.filter(is_purchased=False).count()
    active_items_count.short_description = 'Active Items'
    
    def purchased_items_count(self, obj):
        return obj.items.filter(is_purchased=True).count()
    purchased_items_count.short_description = 'Purchased Items'


@admin.register(GroceryItem)
class GroceryItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'grocery_list', 'quantity', 'category', 'is_purchased', 'added_by', 'created_at']
    list_filter = ['is_purchased', 'category', 'created_at']
    search_fields = ['name', 'notes', 'grocery_list__name']
    raw_id_fields = ['grocery_list', 'added_by', 'purchased_by']