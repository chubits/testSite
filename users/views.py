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
from socket import timeout as SocketTimeout

# Django
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.db import OperationalError
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
            if not settings.EMAIL_HOST_USER or not settings.EMAIL_HOST_PASSWORD:
                messages.error(
                    request,
                    "Письмо не отправлено: в .env не заполнены EMAIL_HOST_USER или EMAIL_HOST_PASSWORD."
                )
                return redirect("password_reset")

            if settings.EMAIL_HOST_PASSWORD == "your-mail-ru-app-password":
                messages.error(
                    request,
                    "Письмо не отправлено: в .env указан шаблонный EMAIL_HOST_PASSWORD. "
                    "Укажите реальный пароль приложения для recovery@kasago.ru."
                )
                return redirect("password_reset")

            email = form.cleaned_data['email']
            users = User.objects.filter(email=email)
            if settings.DEBUG:
                domain = request.get_host()
                protocol = 'https' if request.is_secure() else 'http'
            else:
                domain = settings.SITE_DOMAIN or request.get_host()
                protocol = settings.SITE_PROTOCOL or ('https' if request.is_secure() else 'http')
            for user in users:
                subject = "Восстановление пароля"
                email_template_name = "users/password_reset_email.txt"
                c = {
                    "email": user.email,
                    'domain': domain,
                    'site_name': 'Ваш сайт',
                    "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                    "user": user,
                    'token': default_token_generator.make_token(user),
                    'protocol': protocol,
                }
                email_content = render_to_string(email_template_name, c)
                try:
                    send_mail(
                        subject,
                        email_content,
                        settings.PASSWORD_RESET_FROM_EMAIL,
                        [user.email],
                        fail_silently=False,
                    )
                except SMTPAuthenticationError:
                    logger.exception("SMTP authentication failed during password reset")
                    messages.error(
                        request,
                        "Не удалось отправить письмо для восстановления пароля: "
                        "ошибка авторизации почтового сервера."
                    )
                    return redirect("password_reset")
                except (ConnectionRefusedError, SocketTimeout, OSError):
                    logger.exception("SMTP connection failed during password reset")
                    messages.error(
                        request,
                        "Не удалось подключиться к почтовому серверу. Проверьте SMTP-хост, порт "
                        "и ограничения провайдера почты."
                    )
                    return redirect("password_reset")
                except Exception:
                    logger.exception("Failed to send password reset email")
                    messages.error(
                        request,
                        "Не удалось отправить письмо для восстановления пароля. Попробуйте позже."
                    )
                    return redirect("password_reset")
            return redirect("password_reset_done")
    else:
        form = PasswordResetRequestForm()
    return render(request, "users/password_reset_form.html", {"form": form})
from .models import Feedback, UserProfile, Deal

logger = logging.getLogger(__name__)


def auth_page(request):
    show_home_page = request.GET.get("home") == "1"

    if request.user.is_authenticated and not show_home_page:
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
                try:
                    user = register_form.save()
                    phone = register_form.cleaned_data.get("phone", "")
                    user_profile, _ = UserProfile.objects.get_or_create(user=user)
                    if phone:
                        user_profile.phone = phone
                        user_profile.save(update_fields=["phone"])

                    login(request, user)
                    messages.success(request, "Регистрация успешна! Добро пожаловать!")
                    return redirect("profile")
                except OperationalError:
                    logger.exception("Database operation failed during registration")
                    messages.error(
                        request,
                        "Регистрация временно недоступна: приложение не может записать данные в базу. "
                        "Проверьте права доступа к SQLite на сервере."
                    )
                except Exception:
                    logger.exception("Unexpected error during registration")
                    messages.error(
                        request,
                        "Не удалось завершить регистрацию. Попробуйте позже."
                    )
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
            "show_dev_warning": not request.user.is_authenticated or show_home_page,
        },
    )


def profile_view(request):
    if not request.user.is_authenticated:
        return redirect("auth")


    # Инициализация форм
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    # Миграция старых данных: телефон хранился в first_name
    if created and request.user.first_name:
        user_profile.phone = request.user.first_name
        user_profile.save(update_fields=["phone"])

    feedback_form = FeedbackForm()
    profile_form = ProfileEditForm(instance=request.user, user_profile=user_profile)

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
            profile_form = ProfileEditForm(request.POST, request.FILES, instance=request.user, user_profile=user_profile)
            if profile_form.is_valid():
                profile_form.save()
                user_profile.last_name = profile_form.cleaned_data["last_name"]
                user_profile.first_name = profile_form.cleaned_data["first_name"]
                user_profile.middle_name = profile_form.cleaned_data["middle_name"]
                user_profile.phone = profile_form.cleaned_data["phone"]
                user_profile.role = profile_form.cleaned_data["role"]
                if profile_form.cleaned_data.get("avatar"):
                    user_profile.avatar = profile_form.cleaned_data["avatar"]
                user_profile.save()
                messages.success(request, "Данные профиля успешно обновлены.")
                return redirect("profile")
            else:
                messages.error(request, "Пожалуйста, исправьте ошибки в профиле.")

    return render(request, "users/profile.html", {
        "user": request.user,
        "user_profile": user_profile,
        "feedback_form": feedback_form,
        "profile_form": profile_form,
        "osago_stats": {
            "total":     OsagoPolicyModel.objects.filter(created_by=request.user).count(),
            "draft":     OsagoPolicyModel.objects.filter(created_by=request.user, status='draft').count(),
            "active":    OsagoPolicyModel.objects.filter(created_by=request.user, status='active').count(),
            "expired":   OsagoPolicyModel.objects.filter(created_by=request.user, status='expired').count(),
            "cancelled": OsagoPolicyModel.objects.filter(created_by=request.user, status='cancelled').count(),
        },
    })


@require_POST
def logout_view(request):
    logout(request)
    return redirect("auth")


# ===================== ОСАГО =====================

from .forms import OsagoPolicyForm
from .models import OsagoPolicy as OsagoPolicyModel


def osago_list(request):
    if not request.user.is_authenticated:
        return redirect("auth")
    policies = OsagoPolicyModel.objects.filter(created_by=request.user).order_by('-created_at')
    return render(request, "users/osago_list.html", {"policies": policies})


def osago_create(request):
    if not request.user.is_authenticated:
        return redirect("auth")
    form = OsagoPolicyForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        policy = form.save(commit=False)
        policy.created_by = request.user
        policy.save()
        messages.success(request, "Полис ОСАГО сохранён.")
        return redirect("osago_list")
    return render(request, "users/osago_form.html", {"form": form, "title": "Новый полис ОСАГО"})


def osago_edit(request, pk):
    if not request.user.is_authenticated:
        return redirect("auth")
    from django.shortcuts import get_object_or_404
    policy = get_object_or_404(OsagoPolicyModel, pk=pk, created_by=request.user)
    form = OsagoPolicyForm(request.POST or None, instance=policy)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Полис обновлён.")
        return redirect("osago_list")
    return render(request, "users/osago_form.html", {"form": form, "title": "Редактирование полиса ОСАГО", "policy": policy})



def dashboard_view(request):
    if not request.user.is_authenticated:
        return redirect("auth")
    # TODO: ограничить доступ (is_staff) после окончания разработки

    from django.db.models import Count, Sum, Q
    from django.db.models.functions import TruncMonth
    import json

    # --- Сводные карточки ---
    total_deals = Deal.objects.count()
    closed_deals = Deal.objects.filter(status='closed').count()
    in_progress_deals = Deal.objects.filter(status='in_progress').count()
    total_amount = Deal.objects.filter(status='closed').aggregate(s=Sum('amount'))['s'] or 0

    brokers_count = UserProfile.objects.filter(role='broker').count()
    agents_count = UserProfile.objects.filter(role='agent').count()

    # --- Статистика по пользователям (брокеры + агенты) ---
    role_profiles = UserProfile.objects.filter(role__in=['broker', 'agent']).select_related('user')
    user_stats = []
    for profile in role_profiles:
        user_deals = Deal.objects.filter(assigned_to=profile.user)
        user_stats.append({
            'profile': profile,
            'total': user_deals.count(),
            'closed': user_deals.filter(status='closed').count(),
            'in_progress': user_deals.filter(status='in_progress').count(),
            'cancelled': user_deals.filter(status='cancelled').count(),
            'amount': user_deals.filter(status='closed').aggregate(s=Sum('amount'))['s'] or 0,
        })
    user_stats.sort(key=lambda x: x['closed'], reverse=True)

    # --- Данные для графика по месяцам (последние 6 месяцев) ---
    from datetime import date, timedelta
    from django.utils import timezone
    six_months_ago = timezone.now() - timedelta(days=182)
    monthly_raw = (
        Deal.objects
        .filter(created_at__gte=six_months_ago)
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )
    chart_labels = [entry['month'].strftime('%b %Y') for entry in monthly_raw]
    chart_data = [entry['count'] for entry in monthly_raw]

    # --- Распределение статусов для пончика ---
    status_counts = {s: Deal.objects.filter(status=s).count() for s, _ in Deal.STATUS_CHOICES}

    # --- Последние 10 сделок ---
    recent_deals = Deal.objects.select_related('assigned_to', 'assigned_to__userprofile').order_by('-created_at')[:10]

    return render(request, "users/dashboard.html", {
        "total_deals": total_deals,
        "closed_deals": closed_deals,
        "in_progress_deals": in_progress_deals,
        "total_amount": total_amount,
        "brokers_count": brokers_count,
        "agents_count": agents_count,
        "user_stats": user_stats,
        "recent_deals": recent_deals,
        "chart_labels": json.dumps(chart_labels, ensure_ascii=False),
        "chart_data": json.dumps(chart_data),
        "status_counts": json.dumps(status_counts),
    })
