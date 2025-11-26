from django.urls import path
from . import views

urlpatterns = [
    # =========================================================
    # I. TEMPLATE RENDERING VIEWS (Visible Frontend Pages)
    # Note: These are accessed via /news/ prefix from config/urls.py
    # =========================================================

    # News Feed Home Page (Requires Template: newsfeed/news_feed.html)
    path('home/', views.HomeView.as_view(), name='home'),

    # Single Article Detail Page (Requires Template: newsfeed/article_detail.html)
    path('article/<int:article_id>/', views.IndividualArticleDetailView.as_view(), name='article_detail'),

    # Authentication Pages (Requires Templates: newsfeed/login.html, newsfeed/signup.html, etc.)
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Forgot Password Flow
    path("forgot-password/", views.forgot_password_view, name="forgot_password"),
    path("forgot-password/question/<int:user_id>/", views.answer_security_question, name="answer_security_question"),
    path("forgot-password/reset/<int:user_id>/", views.reset_password_security, name="reset_password_security"),

    # =========================================================
    # II. API ENDPOINTS (For Data Exchange - JS se call honge)
    # =========================================================

    # Article Filtering API (Returns JSON data)
    path('filter_article/<int:category_id>/', views.FilterArticleDetailView.as_view(), name='filter_article'),

    # User Profile API (Returns JSON data)
    path('profile/', views.UserProfile.as_view(), name='profile'),

    # Like/Unlike Article API (Toggle)
    path('like/<int:article_id>/', views.LikeArticle.as_view(), name='like_article'),

    # Comment Article API
    path('comment/<int:article_id>/', views.CommentArticle.as_view(), name='comment_article'),
    # Name corrected from save_article in your original code

    # Save/Unsave Article API (Toggle)
    path('save/<int:article_id>/', views.SaveArticle.as_view(), name='save_article'),

    # Admin Article CRUD API
    path('admin/article/crud/', views.CreateArticle.as_view(), name='create_article'),
]