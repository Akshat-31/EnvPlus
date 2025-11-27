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
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.security_question=form.cleaned_data['security_question']
            user.set_security_answer(form.cleaned_data['security_answer'])
            user.set_password(form.cleaned_data['password'])
            user.save()
            return redirect('login')
    else:
        form = SignupForm()
    return render(request, "newsfeed/signup.html", {"form": form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        print("POST DATA:", request.POST)
        if form.is_valid():
            username=form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            print("User is ::",user)
            print("password is ::",password)
            if user:
                print("I AMA HEER")
                login(request, user)
                user.last_login_count += 1
                user.save()
                LoginHistory.objects.create(user=user)
                response = redirect('home')
                response.set_cookie('last_visit', user.last_login.isoformat())
                return response
            else:
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
                    return render(request, "newsfeed/forgot_password.html", {"form": form,"error": "User not found."})

            return redirect("answer_security_question", user_id=user.id)
    else:
        form = SecurityQuestionForm()

    return render(request, "newsfeed/forgot_password.html", {"form": form})

def answer_security_question(request, user_id):
    user = User.objects.get(id=user_id)

    if request.method == "POST":
        form = AnswerSecurityQuestionForm(request.POST)
        if form.is_valid():
            if user.check_security_answer(form.cleaned_data["answer"]):
                return redirect("reset_password_security", user_id=user.id)
            else:
                return render(request, "newsfeed/answer_security_question.html", {
                    "form": form,
                    "question": user.security_question,
                    "error": "Incorrect answer.",
                    "user_id":user.id
                })
    else:
        form = AnswerSecurityQuestionForm()
    return render(request, "newsfeed/answer_security_question.html", {
        "form": form,
        "question": user.security_question,
        "user_id":user.id
    })

def reset_password_security(request, user_id):
    user = User.objects.get(id=user_id)
    if request.method == "POST":
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            user.set_password(form.cleaned_data["new_password1"])
            user.save()
            form=LoginForm()
            return redirect("login")
    else:
        form = ResetPasswordForm()
    return render(request, "newsfeed/reset_password_security.html", {"form": form,"user_id":user.id})

class HomeView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        print("User is::", request.user)
        user = request.user if request.user.is_authenticated else None

        articles=Article.objects.annotate(
            authorName=F('author__username'),
            like_count=Count('likes', distinct=True),
            comment_count=Count('comments', distinct=True)
            )
        categories=Category.objects.all()
        userLiked=Like.objects.filter(user=user)
        userCommeted=Comment.objects.filter(user=user)
        userHistory=ReadHistory.objects.filter(user=user)
        response={
            'articles':ArticleSerializer(articles,many=True).data,
            'categories':CategorySerializer(categories,many=True).data,
            'userLiked':LikeSerializer(userLiked,many=True).data,
            'userCommeted':CommentSerializer(userCommeted,many=True).data,
            'userHistory':ReadHistorySerializer(userHistory, many=True).data
        }
        print("HOME RESPONSE::", response['articles'])
        return render(request, 'newsfeed/home.html', response)

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
            if request.user == article.author:
                print("YYYYYYYYYYYYYYYYY")
                response["edit_permission"]=True
            print("Resppnse is ::", response)
            return render(request, 'newsfeed/articledetail.html', response)
        
        except Article.DoesNotExist:
            return redirect('home')
        
class FilterArticleDetailView(APIView):

    def get(self, request, category_id):
        try:
            article= Article.objects.filter(category__id=category_id)
            response={
                'articles':ArticleSerializer(article,many=True).data
            }
            return render(request, 'newsfeed/home.html', response)
        except Article.DoesNotExist:
            return redirect('home')
    
class SearchNewsDetailView(APIView):

    def get(self, request):
        try:
            query = request.GET.get("query", "")
            if query:
                results=Article.objects.filter(title__icontains=query)
            else:
                results=Article.objects.filter(title__icontains="Nothing")
            response={
                'articles':ArticleSerializer(results,many=True).data
            }
            return render(request, 'newsfeed/home.html', response)
        except Article.DoesNotExist:
            return redirect('home')

class UserProfile(APIView):

    def get(self, request):
        user = request.user if request.user.is_authenticated else None
        userLiked=Like.objects.filter(user=user)
        userCommeted=Comment.objects.filter(user=user)
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
        print("Te",ArticleSavedSerializer(userSaved,many=True).data)
        return render(request, 'newsfeed/profile.html', response)

class LikeArticle(APIView):
    def post(self, request, article_id):
        user = request.user if request.user.is_authenticated else None
        
        like_records=Like.objects.filter(user=user, article__id=article_id)
        if like_records:
            return redirect('home')
        else:
            article=Article.objects.get(id=article_id)
            l=Like.objects.create(user=user, article=article)
            l.save()
            return redirect('home')

class CommentArticle(APIView):

    def post(self, request, article_id):
        try:
            user = request.user if request.user.is_authenticated else None
            print("Data received is ::", request.data.get("content"))
            
            like_records=Comment.objects.filter(user=user, article__id=article_id)
            if like_records:
                return redirect('article_detail', article_id=article.id)
            else:
                article=Article.objects.get(id=article_id)
                Comment.objects.create(user=user, article=article, content=request.data.get("content"))
                return redirect('article_detail', article_id=article.id)
        except Exception as e:
            print("Exception as::",e)
            return redirect('home')

class SaveArticle(APIView):

    def post(self, request, article_id):
        try:
            user = request.user if request.user.is_authenticated else None
            print("Data received is ::", request.data.get("content"))
            
            like_records=SavedArticle.objects.filter(user=user, article__id=article_id)
            if like_records:
                return redirect('home')
            else:
                article=Article.objects.get(id=article_id)
                SavedArticle.objects.create(user=user, article=article)
                return redirect(request.META.get('HTTP_REFERER', 'article_detail', kwargs={'article_id': article.id}))
        except Exception as e:
            print("Exception as::",e)
            return redirect('home')

class CreateArticle(APIView):

    def post(self, request):
        try:
            print("Request::",request)
            print("Comand ks::",request.data.get('command',None) )
            if request.data.get('command',None)=='delete':
                return self.delete(request)
            if request.GET.get("id", None):
                return self.put(request)

            article_title=request.data.get('title')
            description=request.data.get('description')
            content=request.data.get('content')
            category=request.data.get('category')
            image=request.FILES.get('image')
            print("IMAGE RECEIVED::", image)
            read_time=request.data.get('read_time',None)
            
            if category:
                category = get_object_or_404(Category, id=category)
            Article.objects.create(title=article_title,description=description,content=content,read_time=read_time,author=request.user, category=category,image=image)
            return redirect('home')
        except Exception as e:
            print("Exception as ::",e)
            return redirect('home')
    
    def put(self, request):
        try:
            print()
            article_id=request.GET.get('id')
            article_title=request.data.get('title')
            description=request.data.get('description')
            content=request.data.get('content')
            category=request.data.get('category')
            read_time=request.data.get('read_time',None)
            image=request.FILES.get('image')
            
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
                if image:
                    article.image = image
                if category:
                    try:
                        category_obj = Category.objects.get(id=category)
                        article.category = category_obj
                    except Category.DoesNotExist:
                        return redirect('home')
                article.save()
                return redirect('home')

            except Article.DoesNotExist:
                    return redirect('home')
        except Exception as e:
            print("Exception as ::",e)
            return redirect('home')
    
    def delete(self,request):
        try:
            article_id=request.data.get('id')
            try:
                article=Article.objects.get(id=article_id)
                article.delete()
                return redirect('home')
            except Article.DoesNotExist:
                    return redirect('home')
        except Exception as e:
            print("Exception as ::",e)
            return redirect('home')
    
    def get(self, request):
        print("AMAMAMAMA:",request.GET.get('id',None))
        if request.GET.get('id',None):
            article_id = request.GET.get("id", None)
            article = Article.objects.get(id=article_id)
            form = ArticleForm(instance=article)
            return render(request, "newsfeed/create_article.html", {
            "form": form,
            "article": article,   
            "edit_mode": True,
        })
        else:
            form = ArticleForm()
        return render(request, "newsfeed/create_article.html",{"form":form})

