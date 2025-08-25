from django.views.generic import ListView, DetailView
from .models import Post


class NewsListView(ListView):
    model = Post
    template_name = 'news/news_list.html'
    context_object_name = 'news_list'
    paginate_by = None

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
