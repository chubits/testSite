import logging

from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.http import require_POST
from smtplib import SMTPAuthenticationError

from .forms import RegisterForm, LoginForm, FeedbackForm
from .models import Feedback

logger = logging.getLogger(__name__)


def auth_page(request):
    if request.user.is_authenticated:
        return redirect("profile")

    register_form = RegisterForm()
    login_form = LoginForm()

    if request.method == "POST":
        if "register" in request.POST:
            register_form = RegisterForm(request.POST)
            if register_form.is_valid():
                user = register_form.save()
                login(request, user)
                messages.success(request, "Регистрация успешна! Добро пожаловать!")
                return redirect("profile")
            else:
                messages.error(request, "Ошибка при регистрации")

        elif "login" in request.POST:
            login_form = LoginForm(data=request.POST)
            if login_form.is_valid():
                user = login_form.get_user()
                login(request, user)
                messages.success(request, "Вы вошли в систему")
                return redirect("profile")
            else:
                messages.error(request, "Неверный логин или пароль")

    return render(
        request,
        "users/auth.html",
        {
            "register_form": register_form,
            "login_form": login_form,
        },
    )


def profile_view(request):
    if not request.user.is_authenticated:
        return redirect("auth")

    feedback_form = FeedbackForm()

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

    return render(request, "users/profile.html", {
        "user": request.user,
        "feedback_form": feedback_form,
    })


@require_POST
def logout_view(request):
    logout(request)
    return redirect("auth")