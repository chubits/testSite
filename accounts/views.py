from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from .forms import RegisterForm, LoginForm


def auth_page(request):
    if request.user.is_authenticated:
        return redirect("profile")  # или куда вам нужно

    register_form = RegisterForm()
    login_form = LoginForm()

    if request.method == "POST":
        if "register" in request.POST:
            register_form = RegisterForm(request.POST)
            if register_form.is_valid():
                user = register_form.save()
                login(request, user)  # сразу логиним после регистрации
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
        "accounts/auth.html",
        {
            "register_form": register_form,
            "login_form": login_form,
        },
    )


def profile_view(request):
    if not request.user.is_authenticated:
        return redirect("auth")
    return render(request, "accounts/profile.html", {"user": request.user})


def logout_view(request):
    logout(request)
    return redirect("auth")
