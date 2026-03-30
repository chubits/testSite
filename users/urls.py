from django.urls import path
from . import views

urlpatterns = [
    path("", views.auth_page, name="auth"),
    path("profile/", views.profile_view, name="profile"),
    path("logout/", views.logout_view, name="logout"),
        path('password_reset/', views.password_reset_request, name='password_reset'),
        path('password_reset/done/', views.password_reset_done, name='password_reset_done'),
        path('reset/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),
    ]
