from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.conf import settings


class AuthTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.auth_url = reverse("auth")
        self.profile_url = reverse("profile")
        self.logout_url = reverse("logout")
        self.user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "StrongPass123!",
        }
        self.user = User.objects.create_user(
            username=self.user_data["username"],
            email=self.user_data["email"],
            password=self.user_data["password"],
        )

    # --- Страница авторизации ---

    def test_auth_page_renders(self):
        response = self.client.get(self.auth_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/auth.html")

    def test_auth_page_redirects_authenticated_user(self):
        self.client.login(
            username=self.user_data["username"],
            password=self.user_data["password"],
        )
        response = self.client.get(self.auth_url)
        self.assertRedirects(response, self.profile_url)

    # --- Вход ---

    def test_login_success(self):
        response = self.client.post(self.auth_url, {
            "username": self.user_data["username"],
            "password": self.user_data["password"],
            "login": "",
        })
        self.assertRedirects(response, self.profile_url)

    def test_login_wrong_password(self):
        response = self.client.post(self.auth_url, {
            "username": self.user_data["username"],
            "password": "WrongPass999!",
            "login": "",
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_login_nonexistent_user(self):
        response = self.client.post(self.auth_url, {
            "username": "nouser",
            "password": "whatever",
            "login": "",
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    # --- Регистрация ---

    def test_register_success(self):
        response = self.client.post(self.auth_url, {
            "username": "newuser",
            "email": "new@example.com",
            "phone": "+79990000000",
            "password1": "StrongPass123!",
            "password2": "StrongPass123!",
            "register": "",
        })
        self.assertRedirects(response, self.profile_url)
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_register_duplicate_username(self):
        response = self.client.post(self.auth_url, {
            "username": self.user_data["username"],
            "email": "other@example.com",
            "phone": "+79990000001",
            "password1": "StrongPass123!",
            "password2": "StrongPass123!",
            "register": "",
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.filter(username=self.user_data["username"]).count(), 1)

    def test_register_password_mismatch(self):
        response = self.client.post(self.auth_url, {
            "username": "mismatch",
            "email": "mm@example.com",
            "phone": "+79990000002",
            "password1": "StrongPass123!",
            "password2": "DifferentPass!",
            "register": "",
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="mismatch").exists())

    # --- Профиль ---

    def test_profile_requires_auth(self):
        response = self.client.get(self.profile_url)
        self.assertRedirects(response, self.auth_url)

    def test_profile_accessible_when_logged_in(self):
        self.client.login(
            username=self.user_data["username"],
            password=self.user_data["password"],
        )
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/profile.html")

    # --- Выход ---

    def test_logout(self):
        self.client.login(
            username=self.user_data["username"],
            password=self.user_data["password"],
        )
        response = self.client.post(self.logout_url)
        self.assertRedirects(response, self.auth_url)
        profile_response = self.client.get(self.profile_url)
        self.assertRedirects(profile_response, self.auth_url)

    def test_logout_via_get(self):
        self.client.login(
            username=self.user_data["username"],
            password=self.user_data["password"],
        )
        response = self.client.get(self.logout_url)
        self.assertEqual(response.status_code, 405)

    def test_session_timeout_settings(self):
        self.assertEqual(settings.SESSION_COOKIE_AGE, 600)
        self.assertTrue(settings.SESSION_SAVE_EVERY_REQUEST)
