from rest_framework import serializers
from .models import Article


class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = [
            "id",
            "title",
            "author",
            "comment",
            "link",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]


class ArticleAutoCreateSerializer(serializers.Serializer):
    url = serializers.URLField(required=True)
    comment = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
        help_text="Optional comment to override the LLM-extracted description.",
    )
