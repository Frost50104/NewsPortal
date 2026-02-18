from rest_framework import serializers
from .models import Post, Author, Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class AuthorSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Author
        fields = ['id', 'username', 'rating']

class PostSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(queryset=Author.objects.all())
    categories = serializers.PrimaryKeyRelatedField(many=True, queryset=Category.objects.all())
    post_type_display = serializers.CharField(source='get_post_type_display', read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'author', 'post_type', 'post_type_display', 'created_at', 'categories', 'title', 'text', 'rating']
        read_only_fields = ['created_at', 'rating']
