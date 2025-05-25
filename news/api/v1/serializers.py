from rest_framework import serializers

from news.models import News


class NewsSerializer(serializers.ModelSerializer):
    """Serializer for News model with full fields"""

    author_username = serializers.ReadOnlyField(source="author.username")
    category_display = serializers.ReadOnlyField(source="get_category_display")
    status_display = serializers.ReadOnlyField(source="get_status_display")
    is_published = serializers.ReadOnlyField()

    class Meta:
        model = News
        fields = [
            "id",
            "title",
            "subtitle",
            "image",
            "content",
            "publication_date",
            "created_at",
            "updated_at",
            "category",
            "category_display",
            "is_pro_content",
            "author",
            "author_username",
            "status",
            "status_display",
            "is_published",
        ]
        read_only_fields = ["created_at", "updated_at", "author"]


class NewsDetailSerializer(NewsSerializer):
    """Extended serializer for news details"""

    class Meta(NewsSerializer.Meta):
        fields = NewsSerializer.Meta.fields


class NewsListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing news"""

    author_username = serializers.ReadOnlyField(source="author.username")
    category_display = serializers.ReadOnlyField(source="get_category_display")

    class Meta:
        model = News
        fields = [
            "id",
            "title",
            "subtitle",
            "image",
            "publication_date",
            "category",
            "category_display",
            "is_pro_content",
            "author_username",
            "is_published",
        ]
