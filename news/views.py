from django.db.models import Q
from django.utils.dateparse import parse_date
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, FormView, View
from django.views.generic.edit import UpdateView as UserUpdateView
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponseRedirect
from django import forms
from django.utils.http import url_has_allowed_host_and_scheme
from urllib.parse import quote as urlquote
from django.utils.translation import gettext_lazy as _
import pytz
from rest_framework import viewsets, permissions
from .models import Post, Author, Category, CategorySubscription
from .serializers import PostSerializer
from .signals import AUTHORS_GROUP


class AuthorPermissionRedirectMixin:
    def handle_no_permission(self):
        request = self.request
        if request.user.is_authenticated:
            messages.warning(request, _('Недостаточно прав для выполнения действия. Станьте автором, чтобы продолжить.'))
            next_url = request.get_full_path()
            become_url = reverse('news:become_author')
            # Append next param
            return redirect(f"{become_url}?next={urlquote(next_url)}")
        # Fallback to default behavior (redirect to login)
        return super().handle_no_permission()


class CategoryDetailView(DetailView):
    model = Category
    template_name = 'news/category_detail.html'
    context_object_name = 'category'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        category = self.object
        posts = category.posts.order_by('-created_at')
        ctx['posts'] = posts
        user = self.request.user
        ctx['is_subscribed'] = False
        if user.is_authenticated:
            ctx['is_subscribed'] = CategorySubscription.objects.filter(user=user, category=category).exists()
        return ctx


class CategorySubscribeView(LoginRequiredMixin, View):
    def post(self, request, pk):
        category = get_object_or_404(Category, pk=pk)
        CategorySubscription.objects.get_or_create(user=request.user, category=category)
        messages.success(request, _('Вы подписались на категорию: %(name)s') % {'name': category.name})
        return HttpResponseRedirect(reverse('news:category_detail', args=[pk]))


class CategoryUnsubscribeView(LoginRequiredMixin, View):
    def post(self, request, pk):
        category = get_object_or_404(Category, pk=pk)
        CategorySubscription.objects.filter(user=request.user, category=category).delete()
        messages.info(request, _('Вы отписались от категории: %(name)s') % {'name': category.name})
        return HttpResponseRedirect(reverse('news:category_detail', args=[pk]))


class ArticleDetailView(DetailView):
    model = Post
    template_name = 'news/article_detail.html'
    context_object_name = 'article'

    def get_queryset(self):
        return Post.objects.filter(post_type=Post.ARTICLE)


class NewsListView(ListView):
    model = Post
    template_name = 'news/news_list.html'
    context_object_name = 'news_list'
    paginate_by = 10

    def get_queryset(self):
        # Only news, newest first
        return (
            Post.objects.filter(post_type=Post.NEWS)
            .order_by('-created_at')
            .only('id', 'title', 'text', 'created_at')
        )


class NewsDetailView(DetailView):
    model = Post
    template_name = 'news/news_detail.html'
    context_object_name = 'news_item'

    def get_queryset(self):
        # Ensure details are only for news type as per requirement
        return Post.objects.filter(post_type=Post.NEWS)


class NewsSearchView(ListView):
    model = Post
    template_name = 'news/news_search.html'
    context_object_name = 'news_list'
    paginate_by = 10

    def get_queryset(self):
        qs = Post.objects.filter(post_type=Post.NEWS).order_by('-created_at')
        title = self.request.GET.get('title')
        author = self.request.GET.get('author')
        date_after = self.request.GET.get('date_after')
        category = self.request.GET.get('category')
        if title:
            qs = qs.filter(title__icontains=title)
        if author:
            qs = qs.filter(author__user__username__icontains=author)
        if date_after:
            d = parse_date(date_after)
            if d:
                qs = qs.filter(created_at__date__gte=d)
        if category:
            qs = qs.filter(categories__id=category)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['categories'] = Category.objects.all()
        ctx['filters'] = {
            'title': self.request.GET.get('title', ''),
            'author': self.request.GET.get('author', ''),
            'date_after': self.request.GET.get('date_after', ''),
            'category': self.request.GET.get('category', ''),
        }
        return ctx


# Профиль пользователя: редактирование (требует аутентификации)
class ProfileUpdateView(LoginRequiredMixin, UserUpdateView):
    model = get_user_model()
    fields = ['first_name', 'last_name', 'email']
    template_name = 'account/profile_form.html'
    success_url = reverse_lazy('news:list')

    def get_object(self, queryset=None):
        return self.request.user


# Возможность стать автором
class BecomeAuthorView(LoginRequiredMixin, FormView):
    template_name = 'account/become_author.html'
    success_url = reverse_lazy('news:list')
    form_class = forms.Form  # simple empty form

    def post(self, request, *args, **kwargs):
        group, _ = Group.objects.get_or_create(name=AUTHORS_GROUP)
        request.user.groups.add(group)
        # Ensure Author object exists for this user
        Author.objects.get_or_create(user=request.user)
        messages.success(request, _('Вы стали автором! Теперь вам доступны создание и редактирование публикаций.'))
        next_url = request.POST.get('next') or request.GET.get('next')
        if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
            return redirect(next_url)
        return redirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        request = self.request
        ctx['next'] = request.GET.get('next', '')
        return ctx


# CRUD для новостей
class NewsCreateView(AuthorPermissionRedirectMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'news.add_post'
    model = Post
    fields = ['title', 'text', 'categories']
    template_name = 'news/news_form.html'
    success_url = reverse_lazy('news:list')

    def form_valid(self, form):
        # Assign current user as author (create Author profile if missing)
        author, _ = Author.objects.get_or_create(user=self.request.user)
        form.instance.author = author
        form.instance.post_type = Post.NEWS
        return super().form_valid(form)


class NewsUpdateView(AuthorPermissionRedirectMixin, PermissionRequiredMixin, UpdateView):
    permission_required = 'news.change_post'
    model = Post
    fields = ['title', 'text', 'categories']
    template_name = 'news/news_form.html'
    success_url = reverse_lazy('news:list')

    def get_queryset(self):
        return Post.objects.filter(post_type=Post.NEWS)


class NewsDeleteView(DeleteView):
    model = Post
    template_name = 'news/news_confirm_delete.html'
    success_url = reverse_lazy('news:list')

    def get_queryset(self):
        return Post.objects.filter(post_type=Post.NEWS)


# CRUD for Articles
class ArticleCreateView(AuthorPermissionRedirectMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'news.add_post'
    model = Post
    fields = ['title', 'text', 'categories']
    template_name = 'news/article_form.html'
    success_url = reverse_lazy('news:list')

    def form_valid(self, form):
        # Assign current user as author (create Author profile if missing)
        author, _ = Author.objects.get_or_create(user=self.request.user)
        form.instance.author = author
        form.instance.post_type = Post.ARTICLE
        return super().form_valid(form)


class ArticleUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = 'news.change_post'
    model = Post
    fields = ['title', 'text', 'categories']
    template_name = 'news/article_form.html'
    success_url = reverse_lazy('news:list')

    def get_queryset(self):
        return Post.objects.filter(post_type=Post.ARTICLE)


class ArticleDeleteView(DeleteView):
    model = Post
    template_name = 'news/article_confirm_delete.html'
    success_url = reverse_lazy('news:list')

    def get_queryset(self):
        return Post.objects.filter(post_type=Post.ARTICLE)


class SetTimezoneView(View):
    def post(self, request):
        tzname = request.POST.get('timezone')
        if tzname in pytz.common_timezones:
            request.session['django_timezone'] = tzname
        return redirect(request.META.get('HTTP_REFERER', '/'))


class NewsViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.filter(post_type=Post.NEWS)
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        author, _ = Author.objects.get_or_create(user=self.request.user)
        serializer.save(author=author, post_type=Post.NEWS)


class ArticlesViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.filter(post_type=Post.ARTICLE)
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        author, _ = Author.objects.get_or_create(user=self.request.user)
        serializer.save(author=author, post_type=Post.ARTICLE)
