from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import GroceryList, GroceryItem
from .serializers import (
    GroceryListSerializer,
    GroceryListDetailSerializer,
    GroceryItemSerializer,
    GroceryItemCreateSerializer,
    GroceryItemUpdateSerializer,
    MarkPurchasedSerializer,
    BulkItemIdsSerializer
)
from apps.usergroups.models import UserGroup


class IsGroupMember(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if isinstance(obj, GroceryList):
            return obj.group.members.filter(id=request.user.id).exists()
        if isinstance(obj, GroceryItem):
            return obj.grocery_list.group.members.filter(id=request.user.id).exists()
        return False


class GroceryListViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, IsGroupMember]
    
    def get_queryset(self):
        return GroceryList.objects.filter(
            group__members=self.request.user
        ).select_related('group').prefetch_related('items')
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return GroceryListDetailSerializer
        return GroceryListSerializer
    
    @action(detail=False, methods=['get'], url_path='by-group/(?P<group_id>[^/.]+)')
    def by_group(self, request, group_id=None):
        group = get_object_or_404(
            UserGroup.objects.filter(members=request.user),
            id=group_id
        )
        grocery_list, created = GroceryList.objects.get_or_create(
            group=group,
            defaults={'name': f"{group.name}'s Grocery List"}
        )
        serializer = GroceryListDetailSerializer(grocery_list)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def active_items(self, request, pk=None):
        grocery_list = self.get_object()
        items = grocery_list.items.filter(is_purchased=False).order_by('-created_at')
        return Response(GroceryItemSerializer(items, many=True).data)
    
    @action(detail=True, methods=['get'])
    def purchased_items(self, request, pk=None):
        grocery_list = self.get_object()
        items = grocery_list.items.filter(is_purchased=True).order_by('-purchased_at')
        return Response(GroceryItemSerializer(items, many=True).data)
    
    @action(detail=True, methods=['post'])
    def clear_purchased(self, request, pk=None):
        grocery_list = self.get_object()
        deleted_count, _ = grocery_list.items.filter(is_purchased=True).delete()
        return Response({'detail': f'Deleted {deleted_count} purchased items.', 'deleted_count': deleted_count})


class GroceryItemViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, IsGroupMember]
    
    def get_queryset(self):
        queryset = GroceryItem.objects.filter(
            grocery_list__group__members=self.request.user
        ).select_related('grocery_list', 'added_by', 'purchased_by')
        
        # Apply filters
        if list_id := self.request.query_params.get('list_id'):
            queryset = queryset.filter(grocery_list_id=list_id)
        if is_purchased := self.request.query_params.get('is_purchased'):
            queryset = queryset.filter(is_purchased=is_purchased.lower() == 'true')
        if category := self.request.query_params.get('category'):
            queryset = queryset.filter(category=category)
        if search := self.request.query_params.get('search'):
            queryset = queryset.filter(name__icontains=search)
        
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'create':
            return GroceryItemCreateSerializer
        if self.action in ['update', 'partial_update']:
            return GroceryItemUpdateSerializer
        return GroceryItemSerializer
    
    def create(self, request, *args, **kwargs):
        grocery_list_id = request.data.get('grocery_list_id') or request.query_params.get('list_id')
        if not grocery_list_id:
            return Response({'detail': 'grocery_list_id is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        grocery_list = get_object_or_404(
            GroceryList.objects.filter(group__members=request.user),
            id=grocery_list_id
        )
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(grocery_list=grocery_list, added_by=request.user)
        
        item = GroceryItem.objects.get(id=serializer.instance.id)
        return Response(GroceryItemSerializer(item).data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def toggle_purchased(self, request, pk=None):
        item = self.get_object()
        item.is_purchased = not item.is_purchased
        
        if item.is_purchased:
            item.purchased_at = timezone.now()
            item.purchased_by = request.user
        else:
            item.purchased_at = None
            item.purchased_by = None
        
        item.save()
        return Response(GroceryItemSerializer(item).data)
    
    @action(detail=True, methods=['post'])
    def mark_purchased(self, request, pk=None):
        item = self.get_object()
        serializer = MarkPurchasedSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        item.is_purchased = serializer.validated_data['is_purchased']
        if item.is_purchased:
            item.purchased_at = timezone.now()
            item.purchased_by = request.user
        else:
            item.purchased_at = None
            item.purchased_by = None
        
        item.save()
        return Response(GroceryItemSerializer(item).data)
    
    @action(detail=False, methods=['post'])
    def bulk_mark_purchased(self, request):
        serializer = BulkItemIdsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        items = self.get_queryset().filter(id__in=serializer.validated_data['item_ids'])
        updated_count = items.update(is_purchased=True, purchased_at=timezone.now(), purchased_by=request.user)
        
        return Response({'detail': f'Marked {updated_count} items as purchased.', 'updated_count': updated_count})
    
    @action(detail=False, methods=['post'])
    def bulk_delete(self, request):
        serializer = BulkItemIdsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        items = self.get_queryset().filter(id__in=serializer.validated_data['item_ids'])
        deleted_count, _ = items.delete()
        
        return Response({'detail': f'Deleted {deleted_count} items.', 'deleted_count': deleted_count})