from django.urls import path
from . import views

urlpatterns = [
    path("", views.auth_page, name="auth"),
    path("profile/", views.profile_view, name="profile"),
    path("logout/", views.logout_view, name="logout"),
]
