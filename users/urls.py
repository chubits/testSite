from django.urls import path
from . import views

urlpatterns = [
    path("", views.auth_page, name="auth"),
    path("profile/", views.profile_view, name="profile"),
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path("osago/", views.osago_list, name="osago_list"),
    path("osago/new/", views.osago_create, name="osago_create"),
    path("osago/<int:pk>/edit/", views.osago_edit, name="osago_edit"),
    path("logout/", views.logout_view, name="logout"),
        path('password_reset/', views.password_reset_request, name='password_reset'),
        path('password_reset/done/', views.password_reset_done, name='password_reset_done'),
        path('reset/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),
    ]
