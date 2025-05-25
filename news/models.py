from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

from plans.models import Vertical

User = get_user_model()


class News(models.Model):
    """
    Model for managing news articles in the JOTA system.
    """

    # Options for status field
    class StatusChoices(models.TextChoices):
        DRAFT = "draft", _("Draft")
        PUBLISHED = "published", _("Published")

    title = models.CharField(_("Title"), max_length=200)
    subtitle = models.CharField(_("Subtitle"), max_length=300, blank=True)
    image = models.ImageField(
        _("Image"), upload_to="news/images/%Y/%m/%d/", blank=True, null=True
    )
    content = models.TextField(_("Content"))
    publication_date = models.DateTimeField(
        _("Publication Date"), blank=True, null=True
    )
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)

    # Using Vertical choices for consistency
    category = models.CharField(
        _("Category"),
        max_length=15,
        choices=Vertical.VerticalChoices.choices,
        default=Vertical.VerticalChoices.POWER,
    )

    is_pro_content = models.BooleanField(
        _("PRO Content"),
        default=False,
        help_text=_("Check this option if content is exclusive for PRO clients."),
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="news_articles",
        verbose_name=_("Author"),
    )
    status = models.CharField(
        _("Status"),
        max_length=10,
        choices=StatusChoices.choices,
        default=StatusChoices.DRAFT,
    )

    class Meta:
        verbose_name = _("Notícia")
        verbose_name_plural = _("Notícias")
        ordering = ["-publication_date", "-created_at"]

    def __str__(self) -> str:
        return self.title

    @property
    def is_published(self) -> bool:
        """Checks if the news article is published."""
        return self.status == self.StatusChoices.PUBLISHED

    @property
    def vertical(self):
        """Returns the corresponding vertical object for this news category"""
        try:
            return Vertical.objects.get(slug=self.category)
        except Vertical.DoesNotExist:
            return None
