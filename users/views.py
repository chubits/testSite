from django.contrib.auth.forms import SetPasswordForm
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth import get_user_model
# === Подтверждение сброса пароля ===
def password_reset_confirm(request, uidb64, token):
    User = get_user_model()
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Пароль успешно изменён. Теперь вы можете войти с новым паролем.')
                return redirect('auth')
        else:
            form = SetPasswordForm(user)
        return render(request, 'users/password_reset_confirm.html', {'form': form})
    else:
        return render(request, 'users/password_reset_invalid.html')

# === Невалидная ссылка сброса пароля ===
def password_reset_invalid(request):
    return render(request, 'users/password_reset_invalid.html')
# === Страница подтверждения отправки письма для сброса пароля ===
def password_reset_done(request):
    return render(request, "users/password_reset_done.html")

# Стандартные библиотеки
import logging
from smtplib import SMTPAuthenticationError

# Django
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

# Локальные
from .forms import RegisterForm, LoginForm, FeedbackForm, PasswordResetRequestForm, ProfileEditForm

# === ВОССТАНОВЛЕНИЕ ПАРОЛЯ ПО EMAIL ===
def password_reset_request(request):
    if request.method == "POST":
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            users = User.objects.filter(email=email)
            for user in users:
                subject = "Восстановление пароля"
                email_template_name = "users/password_reset_email.txt"
                c = {
                    "email": user.email,
                    'domain': request.get_host(),
                    'site_name': 'Ваш сайт',
                    "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                    "user": user,
                    'token': default_token_generator.make_token(user),
                    'protocol': 'https' if request.is_secure() else 'http',
                }
                email_content = render_to_string(email_template_name, c)
                send_mail(subject, email_content, settings.DEFAULT_FROM_EMAIL, [user.email])
            return redirect("password_reset_done")
    else:
        form = PasswordResetRequestForm()
    return render(request, "users/password_reset_form.html", {"form": form})
from .models import Feedback

logger = logging.getLogger(__name__)


def auth_page(request):
    if request.user.is_authenticated:
        return redirect("profile")

    register_form = RegisterForm()
    login_form = LoginForm()
    show_login_modal = False
    show_register_modal = False


    if request.method == "POST":
        if "register" in request.POST:
            register_form = RegisterForm(request.POST)
            show_register_modal = True
            if register_form.is_valid():
                user = register_form.save()
                login(request, user)
                messages.success(request, "Регистрация успешна! Добро пожаловать!")
                return redirect("profile")
            else:
                messages.error(request, "Ошибка при регистрации")

        elif "login" in request.POST:
            login_form = LoginForm(data=request.POST)
            show_login_modal = True
            if login_form.is_valid():
                user = login_form.get_user()
                login(request, user)
                return redirect("profile")
            else:
                messages.error(request, "Неверный логин или пароль")

    return render(
        request,
        "users/auth.html",
        {
            "register_form": register_form,
            "login_form": login_form,
            "show_login_modal": show_login_modal,
            "show_register_modal": show_register_modal,
        },
    )


def profile_view(request):
    if not request.user.is_authenticated:
        return redirect("auth")


    # Инициализация форм
    feedback_form = FeedbackForm()
    profile_form = ProfileEditForm(instance=request.user, initial={"phone": request.user.first_name})

    if request.method == "POST":
        if "feedback" in request.POST:
            feedback_form = FeedbackForm(request.POST)
            if feedback_form.is_valid():
                feedback = feedback_form.save(commit=False)
                feedback.user = request.user
                feedback.save()
                subject = f'Новое предложение от {request.user.username} — {feedback.subject}'
                message = (
                    f"Пользователь: {request.user.username} ({request.user.email})\n"
                    f"Тема: {feedback.subject}\n\n"
                    f"Сообщение:\n{feedback.message}\n\n"
                    f"Дата: {feedback.created_at}"
                )
                try:
                    send_mail(
                        subject=subject,
                        message=message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[settings.FEEDBACK_RECIPIENT_EMAIL],
                        fail_silently=False,
                    )
                    messages.success(request, "Спасибо! Предложение отправлено на почту и сохранено.")
                except SMTPAuthenticationError:
                    logger.exception("SMTP authentication failed")
                    messages.error(
                        request,
                        "Предложение сохранено в базу, но письмо не отправлено: "
                        "ошибка авторизации почтового сервера."
                    )
                except Exception:
                    logger.exception("Failed to send feedback email")
                    messages.error(
                        request,
                        "Предложение сохранено в базу, но письмо не удалось отправить. "
                        "Попробуйте позже."
                    )
                return redirect("profile")
            else:
                messages.error(request, "Пожалуйста, исправьте ошибки в форме.")
        elif "edit_profile" in request.POST:
            profile_form = ProfileEditForm(request.POST, instance=request.user)
            if profile_form.is_valid():
                user = profile_form.save(commit=False)
                user.first_name = profile_form.cleaned_data["phone"]
                user.save()
                messages.success(request, "Данные профиля успешно обновлены.")
                return redirect("profile")
            else:
                messages.error(request, "Пожалуйста, исправьте ошибки в профиле.")

    return render(request, "users/profile.html", {
        "user": request.user,
        "feedback_form": feedback_form,
        "profile_form": profile_form,
    })


@require_POST
def logout_view(request):
    logout(request)
    return redirect("auth")