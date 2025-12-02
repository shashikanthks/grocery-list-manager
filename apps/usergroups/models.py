from django.db import models
from django.conf import settings


class UserGroup(models.Model):
    """
    Represents a household/family group that shares grocery lists.
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, default='')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_groups'
    )
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='GroupMembership',
        related_name='user_groups'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_groups'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class GroupMembership(models.Model):
    """
    Represents membership of a user in a user group.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='group_memberships'
    )
    group = models.ForeignKey(
        UserGroup,
        on_delete=models.CASCADE,
        related_name='memberships'
    )
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'group_memberships'
        unique_together = ['user', 'group']
        ordering = ['-joined_at']

    def __str__(self):
        return f"{self.user.username} in {self.group.name}"