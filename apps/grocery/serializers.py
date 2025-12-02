from rest_framework import serializers
from django.utils import timezone
from .models import GroceryList, GroceryItem
from apps.users.serializers import UserMinimalSerializer


class GroceryItemSerializer(serializers.ModelSerializer):
    added_by = UserMinimalSerializer(read_only=True)
    purchased_by = UserMinimalSerializer(read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    
    class Meta:
        model = GroceryItem
        fields = [
            'id', 'name', 'quantity', 'category', 'category_display',
            'notes', 'is_purchased', 'purchased_at',
            'purchased_by', 'added_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'added_by', 'purchased_by', 'purchased_at', 'created_at', 'updated_at']


class GroceryItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroceryItem
        fields = ['name', 'quantity', 'category', 'notes']


class GroceryItemUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroceryItem
        fields = ['name', 'quantity', 'category', 'notes', 'is_purchased']
    
    def update(self, instance, validated_data):
        is_purchased = validated_data.get('is_purchased')
        if is_purchased is not None and is_purchased != instance.is_purchased:
            if is_purchased:
                validated_data['purchased_at'] = timezone.now()
                validated_data['purchased_by'] = self.context['request'].user
            else:
                validated_data['purchased_at'] = None
                validated_data['purchased_by'] = None
        return super().update(instance, validated_data)


class GroceryListSerializer(serializers.ModelSerializer):
    active_items_count = serializers.SerializerMethodField()
    purchased_items_count = serializers.SerializerMethodField()
    
    class Meta:
        model = GroceryList
        fields = ['id', 'name', 'group', 'active_items_count', 'purchased_items_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'group', 'created_at', 'updated_at']
    
    def get_active_items_count(self, obj):
        return obj.items.filter(is_purchased=False).count()
    
    def get_purchased_items_count(self, obj):
        return obj.items.filter(is_purchased=True).count()


class GroceryListDetailSerializer(GroceryListSerializer):
    active_items = serializers.SerializerMethodField()
    purchased_items = serializers.SerializerMethodField()
    
    class Meta(GroceryListSerializer.Meta):
        fields = GroceryListSerializer.Meta.fields + ['active_items', 'purchased_items']
    
    def get_active_items(self, obj):
        items = obj.items.filter(is_purchased=False).order_by('-created_at')
        return GroceryItemSerializer(items, many=True).data
    
    def get_purchased_items(self, obj):
        items = obj.items.filter(is_purchased=True).order_by('-purchased_at')
        return GroceryItemSerializer(items, many=True).data


class MarkPurchasedSerializer(serializers.Serializer):
    is_purchased = serializers.BooleanField()


class BulkItemIdsSerializer(serializers.Serializer):
    item_ids = serializers.ListField(child=serializers.IntegerField(), min_length=1)