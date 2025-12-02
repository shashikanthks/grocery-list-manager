from django.contrib import admin
from .models import UserGroup, GroupMembership


class GroupMembershipInline(admin.TabularInline):
    model = GroupMembership
    extra = 1
    raw_id_fields = ['user']


@admin.register(UserGroup)
class UserGroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_by', 'members_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'description']
    raw_id_fields = ['created_by']
    inlines = [GroupMembershipInline]
    
    def members_count(self, obj):
        return obj.members.count()
    members_count.short_description = 'Members'


@admin.register(GroupMembership)
class GroupMembershipAdmin(admin.ModelAdmin):
    list_display = ['user', 'group', 'joined_at']
    list_filter = ['joined_at', 'group']
    raw_id_fields = ['user', 'group']