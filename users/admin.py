from django.contrib import admin

from .models import Feedback, UserProfile, Deal, OsagoPolicy


@admin.register(OsagoPolicy)
class OsagoPolicyAdmin(admin.ModelAdmin):
    list_display = ("__str__", "status", "insurer_name", "premium_amount", "policy_start", "policy_end", "created_by", "created_at")
    list_filter = ("status", "vehicle_category", "drivers_type")
    search_fields = ("insured_last_name", "insured_first_name", "vehicle_plate", "vehicle_vin", "policy_number")
    date_hierarchy = "created_at"


@admin.register(Deal)
class DealAdmin(admin.ModelAdmin):
    list_display = ("title", "status", "amount", "assigned_to", "created_at", "closed_at")
    list_filter = ("status", "assigned_to")
    search_fields = ("title", "assigned_to__username", "notes")
    date_hierarchy = "created_at"


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "last_name", "first_name", "middle_name", "phone", "role")
    list_filter = ("role",)
    search_fields = ("user__username", "last_name", "first_name", "phone")


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ("user", "subject", "created_at")
    list_filter = ("created_at",)
    search_fields = ("subject", "message", "user__username")
    readonly_fields = ("user", "subject", "message", "created_at")
