from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User as AuthUser
from django.contrib import messages
from newsfeed.forms import *
from newsfeed.models import Article, Category, Like, Comment, ReadHistory, SavedArticle, LoginHistory, User
from django.db.models import Count, F
from django.views import View
from django.http import Http404, JsonResponse

# DRF Imports for API Views
from newsfeed.serializers import *
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView


# =========================================================
# I. AUTHENTICATION / FORM VIEWS
# =========================================================

def signup_view(request):
    form = SignupForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request, "Account created successfully! Please log in.")
        return redirect('login')
    return render(request, "newsfeed/signup.html", {"form": form})


def login_view(request):
    # FIX: Agar user already authenticated hai, toh seedhe home par redirect karo.
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)

                try:
                    user_profile = User.objects.get(id=user.id)
                    user_profile.last_login_count += 1
                    user_profile.save()
                    LoginHistory.objects.create(user=user_profile)
                except User.DoesNotExist:
                    pass

                response = redirect('home')
                return response

            # Agar login fail ho, toh error message dikhao aur login page par raho
            messages.error(request, "Invalid username or password.")
            return redirect('login')

    else:
        form = LoginForm()
    return render(request, 'newsfeed/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("login")


def forgot_password_view(request):
    if request.method == "POST":
        form = SecurityQuestionForm(request.POST)
        if form.is_valid():
            value = form.cleaned_data["username_or_email"]
            try:
                user = AuthUser.objects.get(username=value)
            except AuthUser.DoesNotExist:
                try:
                    user = AuthUser.objects.get(email=value)
                except AuthUser.DoesNotExist:
                    return render(request, "newsfeed/forgot_password.html", {
                        "form": form,
                        "error": "User not found."
                    })
            return redirect("answer_security_question", user_id=user.id)
    else:
        form = SecurityQuestionForm()
    return render(request, "newsfeed/forgot_password.html", {"form": form})


def answer_security_question(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == "POST":
        form = AnswerSecurityQuestionForm(request.POST)
        if form.is_valid():
            if user.check_security_answer(form.cleaned_data["answer"]):
                return redirect("reset_password_security", user_id=user.id)
            else:
                return render(request, "newsfeed/answer_security_question.html", {
                    "form": form,
                    "question": user.get_security_question_display(),
                    "error": "Incorrect answer."
                })
    else:
        form = AnswerSecurityQuestionForm()
    return render(request, "newsfeed/answer_security_question.html", {
        "form": form,
        "question": user.get_security_question_display(),
    })


def reset_password_security(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == "POST":
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            user.set_password(form.cleaned_data["new_password1"])
            user.save()
            return render(request, "newsfeed/reset_password_success.html")
    else:
        form = ResetPasswordForm()
    return render(request, "newsfeed/reset_password_security.html", {"form": form})


# =========================================================
# II. TEMPLATE RENDERING VIEWS
# =========================================================
class HomeView(View):
    """Renders the news feed template by fetching articles and categories."""

    def get(self, request):
        articles = Article.objects.annotate(
            authorName=F('author__username'),
            like_count=Count('likes', distinct=True),
            comment_count=Count('comments', distinct=True)
        ).filter(is_published=True).order_by('-id')

        categories = Category.objects.all()

        context = {
            'articles': articles,
            'categories': categories,
        }

        return render(request, 'newsfeed/news_feed.html', context)


class IndividualArticleDetailView(View):
    """Renders the single article detail page."""

    def get(self, request, article_id):
        try:
            article = Article.objects.annotate(
                authorName=F('author__username'),
                like_count=Count('likes', distinct=True),
                comment_count=Count('comments', distinct=True)
            ).get(id=article_id)
        except Article.DoesNotExist:
            raise Http404("Article Does Not Exist")

        is_liked = False
        is_saved = False

        if request.user.is_authenticated:
            try:
                user_profile = User.objects.get(id=request.user.id)
                ReadHistory.objects.get_or_create(user=user_profile, article=article)
                is_liked = Like.objects.filter(user=request.user, article=article).exists()
                is_saved = SavedArticle.objects.filter(user=request.user, article=article).exists()
            except User.DoesNotExist:
                pass

        context = {
            'article': article,
            'is_liked': is_liked,
            'is_saved': is_saved,
        }

        return render(request, 'newsfeed/article_detail.html', context)


class UserProfileTemplateView(View):
    """Renders the user dashboard template."""

    def get(self, request):
        if not request.user.is_authenticated:
            messages.warning(request, "You need to log in to view your profile.")
            return redirect('login')

        return render(request, 'newsfeed/profile.html', {})


class FilterArticleDetailView(APIView):
    """Returns filtered articles by category as JSON data (API)."""

    def get(self, request, category_id):
        try:
            article = Article.objects.filter(category__id=category_id)
            response = {
                'filtered_article': ArticleSerializer(article, many=True).data
            }
            return Response(response)
        except Article.DoesNotExist:
            return Response({"message": "Article Doesnot Exist"})


# =========================================================
# III. API VIEWS (Data Exchange - For JavaScript)
# =========================================================
class UserProfile(APIView):
    """API to return detailed user profile information and history as JSON."""

    def get(self, request):
        user = request.user
        if not user or not user.is_authenticated:
            return Response({"message": "Authentication required"}, status=401)

        user_profile_data = get_object_or_404(User, id=user.id)

        userLiked = Like.objects.filter(user=user_profile_data)
        userCommeted = Comment.objects.filter(user=user_profile_data)
        userReadHistory = ReadHistory.objects.filter(user=user_profile_data)
        userSaved = SavedArticle.objects.filter(user=user_profile_data)
        userLoginHistory = LoginHistory.objects.filter(user=user_profile_data).order_by('-created_at')[:5]

        response = {
            'user_detail': UserDetailSerializer(user_profile_data).data,
            'userLiked_count': userLiked.count(),
            'userCommeted_count': userCommeted.count(),
            'userSaved_count': userSaved.count(),
            'userReadHistory_count': userReadHistory.count(),
            'userLoginHistory': LoginHistorySerializer(userLoginHistory, many=True).data
        }
        return Response(response)


class LikeArticle(APIView):
    def post(self, request, article_id):
        user = request.user if request.user.is_authenticated else None
        if not user or not user.is_authenticated:
            return Response({"message": "Authentication required"}, status=401)

        like_records = Like.objects.filter(user=user, article__id=article_id)
        if like_records.exists():
            like_records.delete()
            return Response({"message": "Article unliked", "action": "unliked"})
        else:
            article = get_object_or_404(Article, id=article_id)
            Like.objects.create(user=user, article=article)
            return Response({"message": "Article is liked", "action": "liked"})


class CommentArticle(APIView):
    def post(self, request, article_id):
        try:
            user = request.user if request.user.is_authenticated else None
            if not user or not user.is_authenticated:
                return Response({"message": "Authentication required"}, status=401)

            content = request.data.get("content")
            if not content:
                return Response({"message": "Content is required"}, status=400)

            article = get_object_or_404(Article, id=article_id)
            Comment.objects.create(user=user, article=article, content=content)
            return Response({"message": "Article is Commented"})
        except Exception as e:
            return Response({"message": f"Error: {e}"})


class SaveArticle(APIView):
    def post(self, request, article_id):
        try:
            user = request.user if request.user.is_authenticated else None
            if not user or not user.is_authenticated:
                return Response({"message": "Authentication required"}, status=401)

            like_records = SavedArticle.objects.filter(user=user, article__id=article_id)
            if like_records.exists():
                like_records.delete()
                return Response({"message": "Article unsaved", "action": "unsaved"})
            else:
                article = get_object_or_404(Article, id=article_id)
                SavedArticle.objects.create(user=user, article=article)
                return Response({"message": "Article is Saved", "action": "saved"})
        except Exception as e:
            return Response({"message": f"Error: {e}"})


class CreateArticle(APIView):
    def post(self, request):
        try:
            article_title = request.data.get('title')
            description = request.data.get('description')
            content = request.data.get('content')
            category = request.data.get('category')
            image = request.FILES.get('image')
            read_time = request.data.get('read_time', None)

            if category:
                category = get_object_or_404(Category, id=category)
            Article.objects.create(title=article_title, description=description, content=content, read_time=read_time,
                                   author=request.user, category=category, image=image)
            return Response({"message": "Article created"})
        except Exception as e:
            return Response({"message": "ERROR"})

    def put(self, request):
        try:
            article_id = request.data.get('id')
            article_title = request.data.get('title')
            description = request.data.get('description')
            content = request.data.get('content')
            category = request.data.get('category')
            read_time = request.data.get('read_time', None)

            try:
                article = Article.objects.get(id=article_id)
                if article_title:
                    article.title = article_title
                if description:
                    article.description = description
                if content:
                    article.content = content
                if read_time:
                    article.read_time = read_time
                if category:
                    try:
                        category_obj = Category.objects.get(id=category)
                        article.category = category_obj
                    except Category.DoesNotExist:
                        return Response({"message": "category Not found"})
                article.save()
                return Response({"message": "Article updated"})

            except Article.DoesNotExist:
                return Response({"message": "Object Not found"})
        except Exception as e:
            return Response({"message": "ERROR"})

    def delete(self, request):
        try:
            article_id = request.data.get('id')
            try:
                article = Article.objects.get(id=article_id)
                article.delete()
                return Response({"message": "Article Delete"})
            except Article.DoesNotExist:
                return Response({"message": "Object Not found"})
        except Exception as e:
            return Response({"message": "ERROR"})