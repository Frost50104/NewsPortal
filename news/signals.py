from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save
from django.db.models.signals import post_migrate
from django.dispatch import receiver

from .models import Post

COMMON_GROUP = 'common'
AUTHORS_GROUP = 'authors'


def ensure_groups_and_permissions():
    # Create groups
    common_group, _ = Group.objects.get_or_create(name=COMMON_GROUP)
    authors_group, _ = Group.objects.get_or_create(name=AUTHORS_GROUP)

    # Ensure authors have add/change permissions for Post
    ct = ContentType.objects.get_for_model(Post)
    perms = Permission.objects.filter(content_type=ct, codename__in=[
        'add_post', 'change_post'
    ])
    for perm in perms:
        authors_group.permissions.add(perm)
    authors_group.save()


@receiver(post_migrate)
def create_groups_on_migrate(sender, **kwargs):
    # ensure groups after migrations for any app
    ensure_groups_and_permissions()


@receiver(post_save, sender=get_user_model())
def add_new_user_to_common(sender, instance, created, **kwargs):
    if created:
        group, _ = Group.objects.get_or_create(name=COMMON_GROUP)
        instance.groups.add(group)
