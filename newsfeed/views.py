from django.shortcuts import render

from newsfeed.forms import *
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate,login,logout

from newsfeed.models import *
from django.db.models import Count,F

from newsfeed.serializers import *
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny



# Create your views here.

def signup_view(request):
    form = SignupForm(request.POST)
    if request.method == "POST":
        try:
            print("I AMA HEER")
            User.objects.get(username=request.user)
        except User.DoesNotExist:
            if form.is_valid():
                form.save()
        return redirect('login')
    return render(request, "newsfeed/signup.html", {"form": form})

def login_view(request):
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
                user.last_login_count += 1
                user.save()
                LoginHistory.objects.create(user=user)
                response = redirect('home')
                response.set_cookie('last_visit', user.last_login.isoformat())
                return response
            return redirect('signup')
    else:
        form = LoginForm()
    
    return render(request, 'newsfeed/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect("login")

def forgot_password_view(request):
    if request.method == "POST":
        form = SecurityQuestionForm(request.POST)
        if form.is_valid():
            value = form.cleaned_data["username_or_email"]

            try:
                user = User.objects.get(username=value)
            except User.DoesNotExist:
                try:
                    user = User.objects.get(email=value)
                except User.DoesNotExist:
                    return render(request, "/forgot_password.html", {
                        "form": form,
                        "error": "User not found."
                    })

            return redirect("answer_security_question", user_id=user.id)

    else:
        form = SecurityQuestionForm()

    return render(request, "accounts/forgot_password.html", {"form": form})

def answer_security_question(request, user_id):
    user = User.objects.get(id=user_id)

    if request.method == "POST":
        form = AnswerSecurityQuestionForm(request.POST)
        if form.is_valid():
            if user.check_security_answer(form.cleaned_data["answer"]):
                return redirect("reset_password_security", user_id=user.id)
            else:
                return render(request, "accounts/answer_security_question.html", {
                    "form": form,
                    "question": user.get_security_question_display(),
                    "error": "Incorrect answer."
                })
    else:
        form = AnswerSecurityQuestionForm()

    return render(request, "accounts/answer_security_question.html", {
        "form": form,
        "question": user.get_security_question_display(),
    })

def reset_password_security(request, user_id):
    user = User.objects.get(id=user_id)

    if request.method == "POST":
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            user.set_password(form.cleaned_data["new_password1"])
            user.save()
            return render(request, "accounts/reset_password_success.html")
    else:
        form = ResetPasswordForm()

    return render(request, "accounts/reset_password_security.html", {"form": form})


class HomeView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        print("User is::", request.user)
        user = request.user if request.user.is_authenticated else None
        #get all articles

        articles=Article.objects.annotate(
            authorName=F('author__username'),
            like_count=Count('likes', distinct=True),
            comment_count=Count('comments', distinct=True)
            )
        #get all categories
        categories=Category.objects.all()
        #get user liked and commented articles
        userLiked=Like.objects.filter(user=user)
        userCommeted=Comment.objects.filter(user=user)
        #get User history
        userHistory=ReadHistory.objects.filter(user=user)
        response={
            'articles':ArticleSerializer(articles,many=True).data,
            'categories':CategorySerializer(categories,many=True).data,
            'userLiked':LikeSerializer(userLiked,many=True).data,
            'userCommeted':CommentSerializer(userCommeted,many=True).data,
            'userHistory':ReadHistorySerializer(userHistory, many=True).data
        }
        return Response(response)

class IndividualArticleDetailView(APIView):

    def get(self, request, article_id):
        try:
            article= Article.objects.get(id=article_id)
            response={
                'article_detail':ArticleSerializer(article).data
            }
            if request.user.is_authenticated:
                user_liked_article=Like.objects.filter(article__id=article_id)
                user_commented_article=Comment.objects.filter(article__id=article_id)
                response["article_like_detail"]=LikeSerializer(user_liked_article,many=True).data
                response["article_comment_detail"]=CommentSerializer(user_commented_article,many=True).data
            return Response(response)
        except Article.DoesNotExist:
            return Response({"message":"Article Doesnot Exist"})
        
class FilterArticleDetailView(APIView):

    def get(self, request, category_id):
        try:
            article= Article.objects.filter(category__id=category_id)
            response={
                'filtered_article':ArticleSerializer(article).data
            }
            return Response(response)
        except Article.DoesNotExist:
            return Response({"message":"Article Doesnot Exist"})

class UserProfile(APIView):

    def get(self, request):
        user = request.user if request.user.is_authenticated else None
        userLiked=Like.objects.filter(user=user)
        userCommeted=Comment.objects.filter(user=user)
        #get User history
        userReadHistory=ReadHistory.objects.filter(user=user)
        userSaved=SavedArticle.objects.filter(user=user)
        userLoginHistory=LoginHistory.objects.filter(user=user)
        response={
            'user_detail':UserDetailSerializer(user).data,
            'userLiked':LikeSerializer(userLiked,many=True).data,
            'userCommeted':CommentSerializer(userCommeted,many=True).data,
            'userSaved':ArticleSavedSerializer(userSaved,many=True).data,
            'userReadHistory':ReadHistorySerializer(userReadHistory, many=True).data,
            'userLoginHistory':LoginHistorySerializer(userLoginHistory, many=True).data
        }
        return Response(response)

class LikeArticle(APIView):

    def post(self, request, article_id):
        user = request.user if request.user.is_authenticated else None
        
        like_records=Like.objects.filter(user=user, article__id=article_id)
        if like_records:
            return Response({"messgae":"This article is already liked"})
        else:
            article=Article.objects.get(id=article_id)
            Like.objects.create(user=user, article=article)
            return Response({"message":"Article is liked"})

class CommentArticle(APIView):

    def post(self, request, article_id):
        try:
            user = request.user if request.user.is_authenticated else None
            print("Data received is ::", request.data.get("content"))
            
            like_records=Comment.objects.filter(user=user, article__id=article_id)
            if like_records:
                return Response({"messgae":"This article is already commented"})
            else:
                article=Article.objects.get(id=article_id)
                Comment.objects.create(user=user, article=article, content=request.data.get("content"))
                return Response({"message":"Article is Commented"})
        except Exception as e:
            print("Exception as::",e)
            return Response({"message":"Error"})

class SaveArticle(APIView):

    def post(self, request, article_id):
        try:
            user = request.user if request.user.is_authenticated else None
            print("Data received is ::", request.data.get("content"))
            
            like_records=SavedArticle.objects.filter(user=user, article__id=article_id)
            if like_records:
                return Response({"messgae":"This article is already saved"})
            else:
                article=Article.objects.get(id=article_id)
                SavedArticle.objects.create(user=user, article=article)
                return Response({"message":"Article is Saved"})
        except Exception as e:
            print("Exception as::",e)
            return Response({"message":"Error"})

class CreateArticle(APIView):

    def post(self, request):
        try:
            article_title=request.data.get('title')
            description=request.data.get('description')
            content=request.data.get('content')
            category=request.data.get('category')
            image=request.FILES.get('image')
            read_time=request.data.get('read_time',None)
            
            if category:
                category = get_object_or_404(Category, id=category)
            Article.objects.create(title=article_title,description=description,content=content,read_time=read_time,author=request.user, category=category,image=image)
            return Response({"message":"Article created"})
        except Exception as e:
            print("Exception as ::",e)
            return Response({"message":"ERROR"})
    
    def put(self, request):
        try:
            article_id=request.data.get('id')
            article_title=request.data.get('title')
            description=request.data.get('description')
            content=request.data.get('content')
            category=request.data.get('category')
            read_time=request.data.get('read_time',None)
            
            try:
                article=Article.objects.get(id=article_id)
                if article_title:
                    article.title=article_title
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
                return Response({"message":"Article updated"})

            except Article.DoesNotExist:
                    return Response({"message":"Object Not found"})
        except Exception as e:
            print("Exception as ::",e)
            return Response({"message":"ERROR"})
    
    def delete(self,request):
        try:
            article_id=request.data.get('id')
            try:
                article=Article.objects.get(id=article_id)
                article.delete()
                return Response({"message":"Article Delete"})
            except Article.DoesNotExist:
                    return Response({"message":"Object Not found"})
        except Exception as e:
            print("Exception as ::",e)
            return Response({"message":"ERROR"})




















    












