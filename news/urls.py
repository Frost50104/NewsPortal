from django.urls import path
from .views import (
    NewsListView,
    NewsDetailView,
    NewsSearchView,
    NewsCreateView, NewsUpdateView, NewsDeleteView,
    ArticleCreateView, ArticleUpdateView, ArticleDeleteView,
    ProfileUpdateView, BecomeAuthorView,
    CategoryDetailView, CategorySubscribeView, CategoryUnsubscribeView,
    ArticleDetailView, SetTimezoneView,
)

app_name = 'news'

urlpatterns = [
    path('', NewsListView.as_view(), name='list'),
    path('search/', NewsSearchView.as_view(), name='search'),

    path('profile/', ProfileUpdateView.as_view(), name='profile_edit'),
    path('become-author/', BecomeAuthorView.as_view(), name='become_author'),

    path('create/', NewsCreateView.as_view(), name='news_create'),
    path('<int:pk>/edit/', NewsUpdateView.as_view(), name='news_edit'),
    path('<int:pk>/delete/', NewsDeleteView.as_view(), name='news_delete'),

    path('articles/create/', ArticleCreateView.as_view(), name='article_create'),
    path('articles/<int:pk>/', ArticleDetailView.as_view(), name='article_detail'),
    path('articles/<int:pk>/edit/', ArticleUpdateView.as_view(), name='article_edit'),
    path('articles/<int:pk>/delete/', ArticleDeleteView.as_view(), name='article_delete'),

    path('categories/<int:pk>/', CategoryDetailView.as_view(), name='category_detail'),
    path('categories/<int:pk>/subscribe/', CategorySubscribeView.as_view(), name='category_subscribe'),
    path('categories/<int:pk>/unsubscribe/', CategoryUnsubscribeView.as_view(), name='category_unsubscribe'),

    path('<int:pk>/', NewsDetailView.as_view(), name='detail'),
    path('set-timezone/', SetTimezoneView.as_view(), name='set_timezone'),
]
