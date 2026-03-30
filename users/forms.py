
from django import forms
from django.contrib.auth.models import User
# Форма для редактирования профиля пользователя
class ProfileEditForm(forms.ModelForm):
    phone = forms.CharField(
        required=True,
        label="Телефон",
        max_length=20,
        widget=forms.TextInput(attrs={"placeholder": "+7 (___) ___-__-__"})
    )

    class Meta:
        model = User
        fields = ("username", "email", "phone")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Логин"
        self.fields["username"].help_text = ""
        self.fields["username"].widget.attrs.update({
            "placeholder": "Логин",
            "readonly": True,
            "class": "profile-username-readonly"
        })
        self.fields["email"].label = "Электронная почта"
        self.fields["email"].widget.attrs.update({"placeholder": "Email"})
        self.fields["phone"].label = "Телефон"
        self.fields["phone"].widget.attrs.update({"placeholder": "+7 (___) ___-__-__"})

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Feedback   # ← новая строка


class RegisterForm(UserCreationForm):

    email = forms.EmailField(
        required=True, widget=forms.EmailInput(attrs={"placeholder": "Email"})
    )
    phone = forms.CharField(
        required=True,
        label="Телефон",
        max_length=20,
        widget=forms.TextInput(attrs={"placeholder": "+7 (___) ___-__-__"})
    )

    class Meta:
        model = User
        fields = ("username", "email", "phone", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Логин"
        self.fields["email"].label = "Электронная почта"
        self.fields["phone"].label = "Телефон"
        self.fields["password1"].label = "Пароль"
        self.fields["password2"].label = "Подтверждение пароля"
        self.fields["username"].help_text = ""
        self.fields["password1"].help_text = ""
        self.fields["password2"].help_text = ""
        self.fields["username"].widget.attrs.update({"placeholder": "Логин"})
        self.fields["email"].widget.attrs.update({"placeholder": "Email"})
        self.fields["phone"].widget.attrs.update({"placeholder": "+7 (___) ___-__-__"})
        self.fields["password1"].widget.attrs.update({"placeholder": "Пароль"})
        self.fields["password2"].widget.attrs.update(
            {"placeholder": "Повторите пароль"}
        )



from django.contrib.auth import authenticate

class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Логин, Email или Телефон"
        self.fields["password"].label = "Пароль"
        self.fields["username"].widget.attrs.update({"placeholder": "Логин / Email / Телефон"})
        self.fields["password"].widget.attrs.update({"placeholder": "Пароль"})

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        if username and password:
            user = authenticate(self.request, username=username, password=password)
            if user is None:
                # Попробуем найти по email
                try:
                    user_obj = User.objects.get(email=username)
                    user = authenticate(self.request, username=user_obj.username, password=password)
                except User.DoesNotExist:
                    user = None
            if user is None:
                # Попробуем найти по телефону (в поле first_name)
                try:
                    user_obj = User.objects.get(first_name=username)
                    user = authenticate(self.request, username=user_obj.username, password=password)
                except User.DoesNotExist:
                    user = None
            if user is None:
                raise forms.ValidationError("Неверный логин, email, телефон или пароль.")
            self.confirm_login_allowed(user)
            self.user_cache = user
        return self.cleaned_data


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

# === ФОРМА ДЛЯ ВОССТАНОВЛЕНИЯ ПАРОЛЯ ===
class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField(label="Введите ваш email", max_length=254)