from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from plans.models import Plan, Subscription, Vertical


@admin.register(Vertical)
class VerticalAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "description"]
    search_fields = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "plan_type", "price", "is_active"]
    list_filter = ["plan_type", "is_active"]
    search_fields = ["name", "description"]
    ordering = ["-id"]


class SubscriptionInline(admin.TabularInline):
    model = Subscription
    extra = 0
    fields = [
        "user",
        "plan",
        "status",  # Corrigido de 'subscription_status' para 'status'
        "start_date",
        "end_date",
        "is_active",
    ]
    readonly_fields = ["is_active"]
    autocomplete_fields = ["user", "plan"]


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "plan",
        "status",  # Corrigido de 'subscription_status' para 'status'
        "start_date",
        "end_date",
        "is_active",
        "auto_renew",
    ]
    list_filter = [
        "status",
        "auto_renew",
        "plan",
    ]  # Corrigido de 'subscription_status' para 'status'
    search_fields = ["user__username", "user__email", "plan__name"]
    date_hierarchy = "start_date"
    autocomplete_fields = ["user", "plan"]
    fieldsets = [
        (None, {"fields": ["user", "plan", "status"]}),  # Corrigido
        (
            _("Date Information"),
            {"fields": ["start_date", "end_date"]},
        ),
        (
            _("Renewal Settings"),
            {"fields": ["auto_renew", "renewal_reminder_sent"]},
        ),
    ]
