from rest_framework import serializers
from .models import UserGroup, GroupMembership
from apps.users.serializers import UserMinimalSerializer


class GroupMembershipSerializer(serializers.ModelSerializer):
    user = UserMinimalSerializer(read_only=True)
    
    class Meta:
        model = GroupMembership
        fields = ['id', 'user', 'joined_at']
        read_only_fields = fields


class UserGroupSerializer(serializers.ModelSerializer):
    created_by = UserMinimalSerializer(read_only=True)
    members_count = serializers.SerializerMethodField()
    
    class Meta:
        model = UserGroup
        fields = ['id', 'name', 'description', 'created_by', 'members_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']
    
    def get_members_count(self, obj):
        return obj.members.count()


class UserGroupDetailSerializer(UserGroupSerializer):
    memberships = GroupMembershipSerializer(many=True, read_only=True)
    
    class Meta(UserGroupSerializer.Meta):
        fields = UserGroupSerializer.Meta.fields + ['memberships']


class AddMemberSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    
    def validate_user_id(self, value):
        from apps.users.models import User
        if not User.objects.filter(id=value).exists():
            raise serializers.ValidationError("User not found.")
        return value