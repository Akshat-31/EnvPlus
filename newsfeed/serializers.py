from rest_framework import serializers
from newsfeed.models import *

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class ArticleSerializer(serializers.ModelSerializer):
    authorName = serializers.CharField(source='author.username',read_only=True)
    like_count = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()

    def get_like_count(self, obj):
        return obj.total_likes()

    def get_comment_count(self, obj):
        return obj.total_comments()

    class Meta:
        model = Article
        fields = [
            'id',
            'title',
            'description',
            'content',
            'image',
            'read_time',
            'views',
            'is_published',
            'authorName',
            'like_count',
            'comment_count',
            'category'
        ]
    
class LikeSerializer(serializers.ModelSerializer):
    article_title = serializers.CharField(source='article.title', read_only=True)

    class Meta:
        model = Like
        fields = ['id', 'article', 'article_title', 'created_at']

class CommentSerializer(serializers.ModelSerializer):
    article_title = serializers.CharField(source='article.title', read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'content', 'article', 'article_title', 'created_at']

class ReadHistorySerializer(serializers.ModelSerializer):
    article_title = serializers.CharField(source='article.title', read_only=True)

    class Meta:
        model = ReadHistory
        fields = ['id', 'article', 'article_title', 'created_at']

class UserDetailSerializer(serializers.ModelSerializer):
     class Meta:
        model = User
        fields = ['bio','id','is_admin','is_author','member_since','last_login_count']

class LoginHistorySerializer(serializers.ModelSerializer):
     class Meta:
        model = LoginHistory
        fields = '__all__'


class ArticleSavedSerializer(serializers.ModelSerializer):
     class Meta:
        model = SavedArticle
        fields = '__all__'
