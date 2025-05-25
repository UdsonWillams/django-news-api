from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

User = get_user_model()

# Constantes
EXPIRATION_REMINDER_DAYS = 7  # Enviar lembrete 7 dias antes da expiração


# Create your models here.
class Vertical(models.Model):
    """Model representing content verticals available in the system"""

    class VerticalChoices(models.TextChoices):
        POWER = "poder", _("Power")
        TAX = "tributos", _("Tax")
        HEALTH = "saude", _("Health")
        ENERGY = "energia", _("Energy")
        LABOR = "trabalhista", _("Labor")

    name = models.CharField(max_length=100, verbose_name=_("Name"))
    slug = models.SlugField(unique=True, choices=VerticalChoices.choices)
    description = models.TextField(blank=True, verbose_name=_("Description"))

    def __str__(self) -> str:
        return (
            self.get_slug_display()
            if self.slug in dict(self.VerticalChoices.choices)
            else self.name
        )

    class Meta:
        verbose_name = _("Vertical")
        verbose_name_plural = _("Verticals")


class Plan(models.Model):
    """Model representing subscription plans that users can purchase"""

    class PlanTypeChoices(models.TextChoices):
        INFO = "info", _("JOTA Info")
        PRO = "pro", _("JOTA PRO")

    name = models.CharField(max_length=100, verbose_name=_("Plan Name"))
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True, verbose_name=_("Description"))
    plan_type = models.CharField(
        max_length=10,
        choices=PlanTypeChoices.choices,
        default=PlanTypeChoices.INFO,
        verbose_name=_("Plan Type"),
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_("Price"),
        help_text=_("Monthly price in BRL"),
    )
    verticals = models.ManyToManyField(
        Vertical,
        related_name="plans",
        blank=True,
        verbose_name=_("Accessible Verticals"),
        help_text=_("Which verticals are included in this plan"),
    )
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))

    # Add trial period option
    has_trial = models.BooleanField(default=False, verbose_name=_("Has Trial Period"))
    trial_days = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Trial Period Days"),
        help_text=_("Number of trial days for this plan"),
    )

    # Add promotional discount
    discount_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name=_("Discount Percentage"),
        help_text=_("Promotional discount percentage"),
    )
    discount_valid_until = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Discount Valid Until"),
    )

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = _("Plan")
        verbose_name_plural = _("Plans")

    @property
    def current_price(self):
        """Return the current price considering any active discount"""
        if (
            self.discount_percent > 0
            and self.discount_valid_until
            and self.discount_valid_until > timezone.now()
        ):
            discount = (self.price * self.discount_percent) / 100
            return self.price - discount
        return self.price


class Subscription(models.Model):
    """Model representing a user's subscription to a specific plan"""

    class StatusChoices(models.TextChoices):
        ACTIVE = "active", _("Active")
        PENDING = "pending", _("Pending")
        CANCELLED = "cancelled", _("Cancelled")
        EXPIRED = "expired", _("Expired")

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="subscriptions",
        verbose_name=_("User"),
    )
    plan = models.ForeignKey(
        Plan,
        on_delete=models.PROTECT,
        related_name="subscriptions",
        verbose_name=_("Plan"),
    )
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.ACTIVE,
        verbose_name=_("Status"),
    )
    start_date = models.DateTimeField(verbose_name=_("Start Date"))
    end_date = models.DateTimeField(blank=True, null=True, verbose_name=_("End Date"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    # Add renewal fields
    auto_renew = models.BooleanField(
        default=True,
        verbose_name=_("Auto Renew"),
        help_text=_("Whether the subscription should automatically renew"),
    )
    renewal_reminder_sent = models.BooleanField(
        default=False, verbose_name=_("Renewal Reminder Sent")
    )

    def __str__(self) -> str:
        return f"{self.user.username} - {self.plan.name}"

    @property
    def is_active(self) -> bool:
        """Check if subscription is active and not expired"""
        return self.status == self.StatusChoices.ACTIVE and (
            self.end_date is None or self.end_date > timezone.now()
        )

    @property
    def days_until_expiration(self):
        """Return the number of days until subscription expires"""
        if not self.end_date:
            return None

        delta = self.end_date - timezone.now()
        return max(0, delta.days)

    def send_expiration_reminder(self):
        """Send a reminder if subscription is about to expire"""
        if (
            self.is_active
            and not self.renewal_reminder_sent
            and self.days_until_expiration is not None
            and self.days_until_expiration <= EXPIRATION_REMINDER_DAYS
        ):
            # Importação local para evitar importação circular
            from .tasks import send_expiration_reminder_email

            # Chamar a tarefa assíncrona para enviar o email
            send_expiration_reminder_email.delay(self.id)
            return True
        return False

    class Meta:
        verbose_name = _("Subscription")
        verbose_name_plural = _("Subscriptions")
        unique_together = ["user", "plan"]
