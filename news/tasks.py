from celery import shared_task
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.conf import settings
from django.core.management import call_command

from .models import Post, CategorySubscription


@shared_task
def send_article_notification(post_id: int, category_ids: list[int]):
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return

    # Build absolute URL and message
    current_site = Site.objects.get_current()
    link = f"https://{current_site.domain}{post.get_absolute_url()}"
    subject = f"Новая статья в ваших категориях: {post.title}"
    preview = post.preview()
    message = f"{preview}\n\nЧитать полностью: {link}"

    emails = set(
        CategorySubscription.objects
        .filter(category_id__in=list(category_ids))
        .values_list('user__email', flat=True)
    )
    emails.discard('')
    emails.discard(None)

    if emails:
        send_mail(subject, message, getattr(settings, 'DEFAULT_FROM_EMAIL', None), list(emails), fail_silently=True)


@shared_task
def send_weekly_digest_task():
    # Reuse existing management command to avoid duplicating business logic
    call_command('send_weekly_digest')
