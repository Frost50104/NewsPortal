from django.db.models import Q
from django.utils.dateparse import parse_date
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, FormView
from django.views.generic.edit import UpdateView as UserUpdateView
from django.shortcuts import redirect
from django.contrib import messages
from .models import Post, Author
from .signals import AUTHORS_GROUP


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
        if title:
            qs = qs.filter(title__icontains=title)
        if author:
            qs = qs.filter(author__user__username__icontains=author)
        if date_after:
            d = parse_date(date_after)
            if d:
                qs = qs.filter(created_at__date__gte=d)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['filters'] = {
            'title': self.request.GET.get('title', ''),
            'author': self.request.GET.get('author', ''),
            'date_after': self.request.GET.get('date_after', ''),
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

    def post(self, request, *args, **kwargs):
        group, _ = Group.objects.get_or_create(name=AUTHORS_GROUP)
        request.user.groups.add(group)
        messages.success(request, 'Вы стали автором! Теперь вам доступны создание и редактирование публикаций.')
        return redirect(self.get_success_url())

    def get(self, request, *args, **kwargs):
        # Simple confirmation page with a button
        return super().get(request, *args, **kwargs)


# CRUD для новостей
class NewsCreateView(PermissionRequiredMixin, CreateView):
    permission_required = 'news.add_post'
    model = Post
    fields = ['title', 'text', 'categories']
    template_name = 'news/news_form.html'
    success_url = reverse_lazy('news:list')

    def form_valid(self, form):
        # In a real app, author should be current user; for simplicity assign first author
        author = Author.objects.first()
        if author is None:
            form.add_error(None, 'Нет доступного автора. Создайте автора в админке.')
            return self.form_invalid(form)
        form.instance.author = author
        form.instance.post_type = Post.NEWS
        return super().form_valid(form)


class NewsUpdateView(PermissionRequiredMixin, UpdateView):
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
class ArticleCreateView(PermissionRequiredMixin, CreateView):
    permission_required = 'news.add_post'
    model = Post
    fields = ['title', 'text', 'categories']
    template_name = 'news/article_form.html'
    success_url = reverse_lazy('news:list')

    def form_valid(self, form):
        author = Author.objects.first()
        if author is None:
            form.add_error(None, 'Нет доступного автора. Создайте автора в админке.')
            return self.form_invalid(form)
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
