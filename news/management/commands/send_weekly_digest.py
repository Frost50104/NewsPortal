from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

from news.models import CategorySubscription, Post


class Command(BaseCommand):
    help = 'Send weekly digest of new articles to users subscribed to categories.'

    def handle(self, *args, **options):
        since = timezone.now() - timedelta(days=7)
        current_site = Site.objects.get_current()

        # Map user_id -> set of Post ids to avoid duplicates across categories
        user_posts = {}

        # Only consider article posts within last week
        recent_articles = (
            Post.objects.filter(post_type=Post.ARTICLE, created_at__gte=since)
            .prefetch_related('categories')
        )
        if not recent_articles.exists():
            self.stdout.write(self.style.WARNING('No recent articles for the last 7 days.'))
            return

        # For each subscription, check if any of the user's categories match article categories
        subs = CategorySubscription.objects.select_related('user', 'category').all()
        # Build mapping category_id -> list of (user_id, user_email)
        cat_to_users = {}
        for s in subs:
            email = (s.user.email or '').strip()
            if not email:
                continue
            cat_to_users.setdefault(s.category_id, []).append((s.user_id, email))

        for article in recent_articles:
            cat_ids = set(article.categories.values_list('id', flat=True))
            for cid in cat_ids:
                for user_id, email in cat_to_users.get(cid, []):
                    user_posts.setdefault((user_id, email), set()).add(article.id)

        # Send emails
        sent = 0
        for (user_id, email), post_ids in user_posts.items():
            posts = Post.objects.filter(id__in=post_ids)
            if not posts:
                continue
            lines = [
                'Новые статьи за неделю:',
                '',
            ]
            for p in posts.order_by('-created_at'):
                link = f"https://{current_site.domain}{p.get_absolute_url()}"
                lines.append(f"- {p.title}: {link}")
            message = "\n".join(lines)
            subject = 'Еженедельный дайджест новых статей'
            send_mail(subject, message, getattr(settings, 'DEFAULT_FROM_EMAIL', None), [email], fail_silently=True)
            sent += 1

        self.stdout.write(self.style.SUCCESS(f'Sent {sent} weekly digests.'))
