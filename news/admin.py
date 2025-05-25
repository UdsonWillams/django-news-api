from django.contrib import admin

from news.models import News


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["title", "content"]
    ordering = ["-created_at"]
