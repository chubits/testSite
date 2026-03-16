from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from smtplib import SMTPAuthenticationError
import time  # для тестового таймаута, если нужно

from .forms import RegisterForm, LoginForm, FeedbackForm
from .models import Feedback


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
        print("DEBUG: Пользователь НЕ авторизован → редирект на auth")
        return redirect("auth")

    print("DEBUG: === profile_view ЗАПУЩЕНА ===")
    feedback_form = FeedbackForm()

    if request.method == "POST":
        print("DEBUG: POST-запрос получен")
        print("DEBUG: Ключи в POST:", list(request.POST.keys()))

        if "feedback" in request.POST:
            print("DEBUG: Кнопка 'feedback' найдена — обрабатываем")
            feedback_form = FeedbackForm(request.POST)

            if feedback_form.is_valid():
                print("DEBUG: Форма ВАЛИДНА!")
                feedback = feedback_form.save(commit=False)
                feedback.user = request.user
                feedback.save()
                print("DEBUG: Сохранено в БД")

                # === ОБНОВЛЁННЫЙ БЛОК ОТПРАВКИ (с таймаутом и детальной ошибкой) ===
                print("DEBUG: Начинаем send_mail...")
                subject = f'Новое предложение от {request.user.username} — {feedback.subject}'
                message = (
                    f"Пользователь: {request.user.username} ({request.user.email})\n"
                    f"Тема: {feedback.subject}\n\n"
                    f"Сообщение:\n{feedback.message}\n\n"
                    f"Дата: {feedback.created_at}"
                )

                try:
                    # Добавляем таймаут на отправку (чтобы не висло вечно)
                    send_mail(
                        subject=subject,
                        message=message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[settings.FEEDBACK_RECIPIENT_EMAIL],
                        fail_silently=False,
                        # timeout=15,  # если Django 4.2+, раскомментируй (в 6.0 может не поддерживаться, используй settings.EMAIL_TIMEOUT)
                    )
                    print("DEBUG: ПИСЬМО УСПЕШНО ОТПРАВЛЕНО!")
                    messages.success(request, "Спасибо! Предложение отправлено на почту и сохранено.")
                except SMTPAuthenticationError as e:
                    print(f"DEBUG: ОШИБКА АВТОРИЗАЦИИ SMTP: {e}")
                    messages.error(
                        request,
                        "Предложение сохранено в базу, но письмо не отправлено: "
                        "Mail.ru требует пароль приложения. Проверьте, что в настройках "
                        "указан пароль приложения, а не обычный пароль ящика."
                    )
                except Exception as e:
                    error_type = type(e).__name__
                    error_msg = str(e)
                    print(f"DEBUG: ОШИБКА ОТПРАВКИ: {error_type} — {error_msg}")
                    messages.error(request, f"Предложение сохранено в базу, но письмо не отправлено: {error_type} — {error_msg[:100]}...")
                return redirect("profile")
            else:
                print("DEBUG: Форма НЕ валидна")
                messages.error(request, "Пожалуйста, исправьте ошибки в форме.")
        else:
            print("DEBUG: 'feedback' НЕ найден в POST!")

    print("DEBUG: Это GET-запрос (показываем форму)")
    return render(request, "users/profile.html", {
        "user": request.user,
        "feedback_form": feedback_form,
    })


def logout_view(request):
    logout(request)
    return redirect("auth")