from django.urls import path
from .views import (
    ArticleAutoCreateAPIView,
    ArticleExtractAPIView,
    ArticleListCreateAPIView,
)

urlpatterns = [
    path(
        "articles/",
        ArticleListCreateAPIView.as_view(),
        name="api-article-list-create",
    ),
    path(
        "articles/auto/",
        ArticleAutoCreateAPIView.as_view(),
        name="api-article-auto-create",
    ),
    path(
        "articles/extract/",
        ArticleExtractAPIView.as_view(),
        name="api-article-extract",
    ),
]
