
from django import forms
from django.contrib.auth.models import User
from .models import UserProfile


MAX_AVATAR_SIZE_BYTES = 5 * 1024 * 1024

# Форма для редактирования профиля пользователя
class ProfileEditForm(forms.ModelForm):
    last_name = forms.CharField(
        required=False,
        label="Фамилия",
        max_length=100,
        widget=forms.TextInput(attrs={"placeholder": "Фамилия"})
    )
    first_name = forms.CharField(
        required=False,
        label="Имя",
        max_length=100,
        widget=forms.TextInput(attrs={"placeholder": "Имя"})
    )
    middle_name = forms.CharField(
        required=False,
        label="Отчество",
        max_length=100,
        widget=forms.TextInput(attrs={"placeholder": "Отчество"})
    )
    phone = forms.CharField(
        required=False,
        label="Телефон",
        max_length=20,
        widget=forms.TextInput(attrs={"placeholder": "+7 (___) ___-__-__"})
    )
    role = forms.ChoiceField(
        required=False,
        label="Роль",
        choices=UserProfile.ROLE_CHOICES,
    )
    avatar = forms.ImageField(
        required=False,
        label="Аватар",
        widget=forms.FileInput(attrs={"accept": "image/*", "class": "avatar-file-input"}),
    )

    class Meta:
        model = User
        fields = ("username", "email")

    def __init__(self, *args, user_profile=None, **kwargs):
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
        if user_profile:
            self.fields["last_name"].initial = user_profile.last_name
            self.fields["first_name"].initial = user_profile.first_name
            self.fields["middle_name"].initial = user_profile.middle_name
            self.fields["phone"].initial = user_profile.phone
            self.fields["role"].initial = user_profile.role

    def clean_avatar(self):
        avatar = self.cleaned_data.get("avatar")
        if avatar and avatar.size > MAX_AVATAR_SIZE_BYTES:
            raise forms.ValidationError("Размер аватара не должен превышать 5 МБ.")
        return avatar

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


# === ФОРМА ПОЛИСА ОСАГО ===
from .models import OsagoPolicy

class OsagoPolicyForm(forms.ModelForm):
    class Meta:
        model = OsagoPolicy
        fields = [
            # Страхователь
            'insured_last_name', 'insured_first_name', 'insured_middle_name',
            'insured_dob', 'insured_phone', 'insured_email',
            # ТС
            'vehicle_make', 'vehicle_model', 'vehicle_year',
            'vehicle_vin', 'vehicle_plate', 'vehicle_category', 'engine_power',
            # Полис
            'drivers_type', 'policy_start', 'policy_end',
            'insurer_name', 'premium_amount', 'policy_number',
            'status', 'notes',
        ]
        widgets = {
            'insured_last_name':   forms.TextInput(attrs={'placeholder': 'Фамилия'}),
            'insured_first_name':  forms.TextInput(attrs={'placeholder': 'Имя'}),
            'insured_middle_name': forms.TextInput(attrs={'placeholder': 'Отчество'}),
            'insured_dob':         forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'insured_phone':       forms.TextInput(attrs={'placeholder': '+7 (___) ___-__-__'}),
            'insured_email':       forms.EmailInput(attrs={'placeholder': 'Email'}),
            'vehicle_make':        forms.TextInput(attrs={'placeholder': 'Toyota, Kia, Lada…'}),
            'vehicle_model':       forms.TextInput(attrs={'placeholder': 'Camry, Rio, Vesta…'}),
            'vehicle_year':        forms.NumberInput(attrs={'placeholder': '2020', 'min': 1900, 'max': 2100}),
            'vehicle_vin':         forms.TextInput(attrs={'placeholder': 'JTDKB20U003XXXXXX', 'maxlength': 20}),
            'vehicle_plate':       forms.TextInput(attrs={'placeholder': 'А123ВС77', 'maxlength': 20}),
            'engine_power':        forms.NumberInput(attrs={'placeholder': 'л.с.', 'min': 1}),
            'policy_start':        forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'policy_end':          forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'insurer_name':        forms.TextInput(attrs={'placeholder': 'Название страховой компании'}),
            'premium_amount':      forms.NumberInput(attrs={'placeholder': '0.00', 'step': '0.01'}),
            'policy_number':       forms.TextInput(attrs={'placeholder': 'ААА 1234567890'}),
            'notes':               forms.Textarea(attrs={'rows': 3, 'placeholder': 'Дополнительные сведения…'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = False
        self.fields['status'].required = True
