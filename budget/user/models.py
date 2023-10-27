from django.db import models
from django.contrib.auth.models import AbstractUser


class MyUser(AbstractUser):
    """Model representing a user."""
    as_group = models.BooleanField(
        default=False,
    )

    group = models.CharField(max_length=50, null=True,
                             default=None, blank=True)

    def get_groups(self):
        """Return list of group objects of which user is a member."""
        groups = UserGroup.objects.filter(members=self.id)
        return groups

    def set_active_group(self, group):
        """Set user to act as a group member."""
        if group in [group.name for group in self.get_groups()]:
            self.group = group
            self.as_group = True

    def get_active_group(self):
        """If user acts as a group member, return the active group."""
        return UserGroup.objects.get(name=self.group)


class UserGroup(models.Model):
    """Model representing a group."""
    name = models.CharField(max_length=50, unique=True)

    nr_of_members = models.SmallIntegerField(default=1)

    members = models.ManyToManyField(MyUser)

    password = models.CharField(max_length=35)


