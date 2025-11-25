from django.contrib import admin
from .models import (
    User, Category, Article, Like, Comment,
    SavedArticle, ReadHistory
)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_admin', 'is_author', 'is_staff')
    search_fields = ('username', 'email')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    search_fields = ('name',)


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('id','title', 'author', 'category', 'is_published', 'views')
    search_fields = ('title', 'author__username')
    list_filter = ('category', 'is_published')


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'article', 'created_at')
    search_fields = ('user__username', 'article__title')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'article', 'created_at')
    search_fields = ('user__username', 'article__title')


@admin.register(SavedArticle)
class SavedArticleAdmin(admin.ModelAdmin):
    list_display = ('user', 'article', 'created_at')
    search_fields = ('user__username', 'article__title')


@admin.register(ReadHistory)
class ReadHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'article', 'read_at')
    search_fields = ('user__username', 'article__title')
