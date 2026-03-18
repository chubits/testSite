from django.contrib import admin

from .models import Feedback


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ("user", "subject", "created_at")
    list_filter = ("created_at",)
    search_fields = ("subject", "message", "user__username")
    readonly_fields = ("user", "subject", "message", "created_at")
