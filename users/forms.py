from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Feedback   # ← новая строка


class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True, widget=forms.EmailInput(attrs={"placeholder": "Email"})
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Логин"
        self.fields["email"].label = "Электронная почта"
        self.fields["password1"].label = "Пароль"
        self.fields["password2"].label = "Подтверждение пароля"
        self.fields["username"].help_text = ""
        self.fields["password1"].help_text = ""
        self.fields["password2"].help_text = ""
        self.fields["username"].widget.attrs.update({"placeholder": "Логин"})
        self.fields["email"].widget.attrs.update({"placeholder": "Email"})
        self.fields["password1"].widget.attrs.update({"placeholder": "Пароль"})
        self.fields["password2"].widget.attrs.update(
            {"placeholder": "Повторите пароль"}
        )


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Логин или Email"
        self.fields["password"].label = "Пароль"
        self.fields["username"].widget.attrs.update({"placeholder": "Логин / Email"})
        self.fields["password"].widget.attrs.update({"placeholder": "Пароль"})


# === НОВАЯ ФОРМА ОБРАТНОЙ СВЯЗИ ===
class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ["subject", "message"]
        widgets = {
            "subject": forms.TextInput(attrs={
                "placeholder": "Тема предложения (например: «Улучшить дизайн главной страницы»)",
                "class": "form-input"
            }),
            "message": forms.Textarea(attrs={
                "placeholder": "Напишите ваши идеи, замечания или предложения по улучшению проекта KOSAGO.RU...",
                "rows": 7,
                "class": "form-input"
            }),
        }
        labels = {
            "subject": "Тема",
            "message": "Ваше предложение",
        }