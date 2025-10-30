from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone


class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0)

    def update_rating(self):
        # Sum of ratings for author's posts * 3
        posts_rating = self.post_set.aggregate(total=models.Sum('rating'))['total'] or 0
        # Sum of ratings for author's comments
        comments_rating = self.user.comment_set.aggregate(total=models.Sum('rating'))['total'] or 0
        # Sum of ratings for comments under author's posts
        comments_on_posts_rating = Comment.objects.filter(post__author=self).aggregate(total=models.Sum('rating'))['total'] or 0
        self.rating = posts_rating * 3 + comments_rating + comments_on_posts_rating
        self.save()

    def __str__(self):
        return f"Author({self.user.username})"


class Category(models.Model):
    name = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return self.name


class CategorySubscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='category_subscriptions')
    category = models.ForeignKey('Category', on_delete=models.CASCADE, related_name='subscriptions')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'category')
        verbose_name = 'Подписка на категорию'
        verbose_name_plural = 'Подписки на категории'

    def __str__(self):
        return f"{self.user.username} -> {self.category.name}"


class Post(models.Model):
    ARTICLE = 'AR'
    NEWS = 'NE'
    POST_TYPES = [
        (ARTICLE, 'article'),
        (NEWS, 'news'),
    ]

    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    post_type = models.CharField(max_length=2, choices=POST_TYPES, default=NEWS)
    created_at = models.DateTimeField(auto_now_add=True)
    categories = models.ManyToManyField(Category, through='PostCategory', related_name='posts')
    title = models.CharField(max_length=255)
    text = models.TextField()
    rating = models.IntegerField(default=0)

    def like(self):
        self.rating = models.F('rating') + 1
        self.save(update_fields=['rating'])
        # refresh value from DB after F-expression
        self.refresh_from_db(fields=['rating'])

    def dislike(self):
        self.rating = models.F('rating') - 1
        self.save(update_fields=['rating'])
        self.refresh_from_db(fields=['rating'])

    def preview(self):
        return (self.text[:124] + '...') if len(self.text) > 124 else self.text

    def get_absolute_url(self):
        if self.post_type == Post.NEWS:
            return reverse('news:detail', args=[self.pk])
        return reverse('news:article_detail', args=[self.pk])

    def __str__(self):
        return f"{self.get_post_type_display()}: {self.title} (rating={self.rating})"


class PostCategory(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('post', 'category')

    def __str__(self):
        return f"{self.post_id} -> {self.category.name}"


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(default=0)

    def like(self):
        self.rating = models.F('rating') + 1
        self.save(update_fields=['rating'])
        self.refresh_from_db(fields=['rating'])

    def dislike(self):
        self.rating = models.F('rating') - 1
        self.save(update_fields=['rating'])
        self.refresh_from_db(fields=['rating'])

    def __str__(self):
        return f"Comment by {self.user.username} on {timezone.localtime(self.created_at).strftime('%Y-%m-%d %H:%M')} (rating={self.rating})"