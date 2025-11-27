from django import forms
from newsfeed.models import Article, Category, User

class SignupForm(forms.ModelForm):
    password=forms.CharField(widget=forms.PasswordInput(attrs={"class": "input"}))
    confirm_password=forms.CharField(widget=forms.PasswordInput(attrs={"class": "input"}))
    security_question=forms.ChoiceField(choices=User.SECURITY_QUESTIONS,widget=forms.Select(attrs={"class": "input"}))
    security_answer = forms.CharField(widget=forms.TextInput(attrs={"class": "input"}))
    class Meta:
        model = User
        fields = ["username", "email", "password"]
        widgets = {
        "username": forms.TextInput(attrs={"class": "input"}),
        "email": forms.EmailInput(attrs={"class": "input"}),
        }

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("password") != cleaned.get("confirm_password"):
            self.add_error("confirm_password", "Passwords do not match")
        if not cleaned.get("security_answer"):
            self.add_error("security_answer", "Please provide an answer")
        return cleaned

class LoginForm(forms.Form):
    username=forms.CharField(widget=forms.TextInput(attrs={"class": "input"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "input"}))
    
class SecurityQuestionForm(forms.Form):
    username_or_email= forms.CharField(label="Username or Email")

class AnswerSecurityQuestionForm(forms.Form):
    answer = forms.CharField(widget=forms.PasswordInput, label="Your Answer")

class ResetPasswordForm(forms.Form):
    new_password1 =forms.CharField(widget=forms.PasswordInput)
    new_password2 = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned = super().clean()
        password_1 = cleaned.get("new_password1")
        password_2 = cleaned.get("new_password2")
        if password_1!=password_2:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned

class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'description', 'content', 'category', 'image', 'read_time']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'input', 'placeholder': 'Article Title'}),
            'description': forms.Textarea(attrs={'class': 'textarea', 'placeholder': 'Brief description'}),
            'content': forms.Textarea(attrs={'class': 'textarea', 'placeholder': 'Full article content'}),
            'category': forms.Select(attrs={'class': 'select'}),
            'read_time': forms.NumberInput(attrs={'class': 'input', 'placeholder': 'Estimated read time in minutes'}),
        }
        labels = {
            'read_time': 'Read Time (minutes)',
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.all().order_by('name')
        self.fields['category'].empty_label = "Select Category"
