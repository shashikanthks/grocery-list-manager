from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import UserGroup, GroupMembership
from .serializers import (
    UserGroupSerializer,
    UserGroupDetailSerializer,
    AddMemberSerializer,
    GroupMembershipSerializer
)
from apps.users.models import User


class UserGroupViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return UserGroup.objects.filter(
            members=self.request.user
        ).prefetch_related('members', 'memberships__user')
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return UserGroupDetailSerializer
        return UserGroupSerializer
    
    def perform_create(self, serializer):
        group = serializer.save(created_by=self.request.user)
        GroupMembership.objects.create(user=self.request.user, group=group)
    
    @action(detail=True, methods=['post'])
    def add_member(self, request, pk=None):
        group = self.get_object()
        serializer = AddMemberSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = get_object_or_404(User, id=serializer.validated_data['user_id'])
        
        if GroupMembership.objects.filter(user=user, group=group).exists():
            return Response(
                {'detail': 'User is already a member of this group.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        membership = GroupMembership.objects.create(user=user, group=group)
        return Response(GroupMembershipSerializer(membership).data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['delete'], url_path='remove_member/(?P<user_id>[^/.]+)')
    def remove_member(self, request, pk=None, user_id=None):
        group = self.get_object()
        user = get_object_or_404(User, id=user_id)
        
        membership = GroupMembership.objects.filter(user=user, group=group).first()
        if not membership:
            return Response({'detail': 'User is not a member of this group.'}, status=status.HTTP_404_NOT_FOUND)
        
        membership.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=True, methods=['post'])
    def leave(self, request, pk=None):
        group = self.get_object()
        membership = GroupMembership.objects.filter(user=request.user, group=group).first()
        
        if not membership:
            return Response({'detail': 'You are not a member of this group.'}, status=status.HTTP_400_BAD_REQUEST)
        
        membership.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)