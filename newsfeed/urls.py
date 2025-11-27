# urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    path("forgot-password/", views.forgot_password_view, name="forgot_password"),
    path("forgot-password/question/<int:user_id>/", views.answer_security_question, name="answer_security_question"),
    path("forgot-password/reset/<int:user_id>/", views.reset_password_security, name="reset_password_security"),
    
    path('home/', views.HomeView.as_view(), name='home'),
    path('article/<int:article_id>/', views.IndividualArticleDetailView.as_view(), name='article_detail'),
    path('filter_article/<int:category_id>/', views.FilterArticleDetailView.as_view(), name='filter_detail'),
    path('filter_news/', views.SearchNewsDetailView.as_view(), name='search_news'),
    path('profile/', views.UserProfile.as_view(), name='profile'),
    
    path('like/<int:article_id>/', views.LikeArticle.as_view(), name='like_article'),
    path('comment/<int:article_id>/', views.CommentArticle.as_view(), name='comment_article'),
    path('save/<int:article_id>/', views.SaveArticle.as_view(), name='save_article'),
    
    path('admin/article/crud/', views.CreateArticle.as_view(), name='create_article'),
]