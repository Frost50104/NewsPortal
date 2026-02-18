from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save, post_migrate, m2m_changed
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.sites.models import Site

from .tasks import send_article_notification

from .models import Post, CategorySubscription

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
        # Welcome email
        if instance.email:
            current_site = Site.objects.get_current()
            subject = 'Добро пожаловать в NewsPortal!'
            message = (
                f"Здравствуйте, {instance.get_username()}!\n\n"
                f"Спасибо за регистрацию в NewsPortal. Вы можете подписываться на любимые категории, "
                f"получать мгновенные уведомления о новых статьях и еженедельные дайджесты.\n\n"
                f"Перейти на сайт: https://{current_site.domain}/\n"
            )
            send_mail(subject, message, getattr(settings, 'DEFAULT_FROM_EMAIL', None), [instance.email], fail_silently=True)


@receiver(m2m_changed, sender=Post.categories.through)
def notify_on_article_in_category(sender, instance: Post, action, reverse, pk_set, **kwargs):
    # Отправляем уведомления асинхронно через Celery, когда статья связана с категориями
    if action != 'post_add':
        return
    if instance.post_type != Post.ARTICLE:
        return
    if not pk_set:
        return

    # Делегируем отправку писем задаче Celery
    try:
        send_article_notification.delay(instance.id, list(pk_set))
    except Exception:
        # В крайнем случае молча игнорируем, чтобы не падать в сигналах
        pass
