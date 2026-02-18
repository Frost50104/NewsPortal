from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from news.views import (
    ArticleCreateView, ArticleUpdateView, ArticleDeleteView,
    NewsViewSet, ArticlesViewSet
)

router = routers.DefaultRouter()
router.register(r'news', NewsViewSet, basename='news-api')
router.register(r'articles', ArticlesViewSet, basename='articles-api')

urlpatterns = [
    path('', include('news.urls', namespace='news')),
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('i18n/', include('django.conf.urls.i18n')),
    path('', include(router.urls)),

    # Article routes at root as per requirement
    path('articles/create/', ArticleCreateView.as_view(), name='article_create_root'),
    path('articles/<int:pk>/edit/', ArticleUpdateView.as_view(), name='article_edit_root'),
    path('articles/<int:pk>/delete/', ArticleDeleteView.as_view(), name='article_delete_root'),
]
