from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name=_('Пользователь'))
    rating = models.IntegerField(default=0, verbose_name=_('Рейтинг'))

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
        return self.user.username

    class Meta:
        verbose_name = _('Автор')
        verbose_name_plural = _('Авторы')


class Category(models.Model):
    name = models.CharField(max_length=64, unique=True, verbose_name=_('Название'))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Категория')
        verbose_name_plural = _('Категории')


class CategorySubscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='category_subscriptions', verbose_name=_('Пользователь'))
    category = models.ForeignKey('Category', on_delete=models.CASCADE, related_name='subscriptions', verbose_name=_('Категория'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата подписки'))

    class Meta:
        unique_together = ('user', 'category')
        verbose_name = _('Подписка на категорию')
        verbose_name_plural = _('Подписки на категории')

    def __str__(self):
        return f"{self.user.username} -> {self.category.name}"


class Post(models.Model):
    ARTICLE = 'AR'
    NEWS = 'NE'
    POST_TYPES = [
        (ARTICLE, _('Статья')),
        (NEWS, _('Новость')),
    ]

    author = models.ForeignKey(Author, on_delete=models.CASCADE, verbose_name=_('Автор'))
    post_type = models.CharField(max_length=2, choices=POST_TYPES, default=NEWS, verbose_name=_('Тип'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата создания'))
    categories = models.ManyToManyField(Category, through='PostCategory', related_name='posts', verbose_name=_('Категории'))
    title = models.CharField(max_length=255, verbose_name=_('Заголовок'))
    text = models.TextField(verbose_name=_('Текст'))
    rating = models.IntegerField(default=0, verbose_name=_('Рейтинг'))

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
        return f"{self.get_post_type_display()}: {self.title}"

    class Meta:
        verbose_name = _('Публикация')
        verbose_name_plural = _('Публикации')


class PostCategory(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, verbose_name=_('Публикация'))
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name=_('Категория'))

    class Meta:
        unique_together = ('post', 'category')
        verbose_name = _('Категория публикации')
        verbose_name_plural = _('Категории публикаций')

    def __str__(self):
        return f"{self.post.title} | {self.category.name}"


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, verbose_name=_('Публикация'))
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('Пользователь'))
    text = models.TextField(verbose_name=_('Текст'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата создания'))
    rating = models.IntegerField(default=0, verbose_name=_('Рейтинг'))

    def like(self):
        self.rating = models.F('rating') + 1
        self.save(update_fields=['rating'])
        self.refresh_from_db(fields=['rating'])

    def dislike(self):
        self.rating = models.F('rating') - 1
        self.save(update_fields=['rating'])
        self.refresh_from_db(fields=['rating'])

    def __str__(self):
        return f"Комментарий от {self.user.username} к {self.post.title}"

    class Meta:
        verbose_name = _('Комментарий')
        verbose_name_plural = _('Комментарии')