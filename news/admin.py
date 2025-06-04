from django.contrib import admin
from django.utils.html import format_html

from news.models import News


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "status", "author", "image_preview", "created_at"]
    list_filter = ["status", "category", "is_pro_content", "created_at"]
    search_fields = ["title", "content", "author__username"]
    ordering = ["-created_at"]
    readonly_fields = ["image_preview"]

    fieldsets = (
        (None, {"fields": ("title", "subtitle", "image", "image_preview")}),
        ("Conteúdo", {"fields": ("content", "category", "is_pro_content")}),
        ("Publicação", {"fields": ("status", "publication_date", "author")}),
    )

    def image_preview(self, obj):
        """Mostra preview da imagem no admin"""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 100px; max-width: 100px;" />',
                obj.image.url,
            )
        return "Sem imagem"

    image_preview.short_description = "Preview da Imagem"
