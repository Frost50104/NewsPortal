from django.contrib import admin
from modeltranslation.admin import TranslationAdmin
from .models import Author, Category, Post, PostCategory, Comment, CategorySubscription


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('user', 'rating')
    list_filter = ('rating',)
    search_fields = ('user__username', 'user__email')


@admin.register(Category)
class CategoryAdmin(TranslationAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(CategorySubscription)
class CategorySubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'category', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('user__username', 'category__name')


class PostCategoryInline(admin.TabularInline):
    model = PostCategory
    extra = 1


@admin.register(Post)
class PostAdmin(TranslationAdmin):
    list_display = ('title', 'author', 'post_type', 'created_at', 'rating')
    list_filter = ('post_type', 'created_at', 'author', 'categories')
    search_fields = ('title', 'text', 'author__user__username')
    inlines = [PostCategoryInline]


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'created_at', 'rating')
    list_filter = ('created_at', 'rating', 'user')
    search_fields = ('text', 'user__username', 'post__title')
