from django import forms
from newsfeed.models import User

class SignupForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "input"}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "input"}))
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
        return cleaned

class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={"class": "input"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "input"}))
    
class SecurityQuestionForm(forms.Form):
    username_or_email = forms.CharField(label="Username or Email")

class AnswerSecurityQuestionForm(forms.Form):
    answer = forms.CharField(widget=forms.PasswordInput, label="Your Answer")

class ResetPasswordForm(forms.Form):
    new_password1 = forms.CharField(widget=forms.PasswordInput)
    new_password2 = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get("new_password1")
        p2 = cleaned.get("new_password2")
        if p1!=p2:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned

