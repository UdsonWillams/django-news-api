from django.contrib.auth.models import AbstractUser, UserManager
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

# Constantes
ONE_HOUR_IN_SECONDS = 60 * 60  # 3600 seconds = 1 hour


class CustomUserManager(UserManager):
    """
    Custom manager para garantir que superusers sejam sempre criados como admin
    """

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault(
            "user_type", "admin"
        )  # Garante que superusers são admin
        return super().create_superuser(username, email, password, **extra_fields)


# Create your models here.
class CustomUser(AbstractUser):
    # User types
    ADMIN = "admin"
    EDITOR = "editor"
    READER = "reader"

    USER_TYPE_CHOICES = [
        (ADMIN, _("Administrator")),
        (EDITOR, _("Editor")),
        (READER, _("Reader")),
    ]

    user_type = models.CharField(
        max_length=10,
        choices=USER_TYPE_CHOICES,
        default=READER,
        verbose_name=_("User Type"),
    )

    # Email should be required and unique
    email = models.EmailField(_("Email address"), unique=True)

    # Add profile picture
    profile_picture = models.ImageField(
        _("Profile Picture"), upload_to="profiles/%Y/%m/", blank=True, null=True
    )

    # Substitui o manager padrão pelo customizado
    objects = CustomUserManager()

    # Helper methods to check user type
    def is_admin(self):
        return self.user_type == self.ADMIN

    def is_editor(self):
        return self.user_type == self.EDITOR

    def is_reader(self):
        return self.user_type == self.READER

    def clean(self):
        """Validate the user model"""
        super().clean()
        if not self.email:
            raise ValidationError({"email": _("Email is required")})

    def get_active_subscription(self):
        """Returns the user's active subscription if any"""
        # Add caching to improve performance
        from django.core.cache import cache

        cache_key = f"user_{self.id}_active_subscription"
        cached_sub = cache.get(cache_key)

        if cached_sub is not None:
            return cached_sub

        subscription = self.subscriptions.filter(
            status="active", end_date__gt=timezone.now()
        ).first()

        # Cache for 1 hour
        cache.set(cache_key, subscription, ONE_HOUR_IN_SECONDS)
        return subscription

    def has_access_to_vertical(self, vertical_slug):
        """Check if user has access to a specific vertical"""
        # Admin and editor have full access
        if self.is_admin() or self.is_editor():
            return True

        # Get active subscription
        subscription = self.get_active_subscription()
        if not subscription:
            return False

        # Check if the vertical is in the plan's verticals
        return subscription.plan.verticals.filter(slug=vertical_slug).exists()

    def can_access_content(self, content):
        """Check if the user can access specific content based on their subscription"""
        # All users can access non-pro content
        if not content.is_pro_content:
            return True

        # Non-readers have full access
        if not self.is_reader():
            return True

        # Check if user has access to the content's category
        return self.has_access_to_vertical(content.category)

    def __str__(self) -> str:
        return f"{self.username} ({self.get_user_type_display()})"
