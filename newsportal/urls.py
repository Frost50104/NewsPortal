from django.contrib import admin
from django.urls import path, include
from news.views import (
    ArticleCreateView, ArticleUpdateView, ArticleDeleteView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('news/', include('news.urls', namespace='news')),

    # Article routes at root as per requirement
    path('articles/create/', ArticleCreateView.as_view(), name='article_create_root'),
    path('articles/<int:pk>/edit/', ArticleUpdateView.as_view(), name='article_edit_root'),
    path('articles/<int:pk>/delete/', ArticleDeleteView.as_view(), name='article_delete_root'),
]
