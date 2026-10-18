import re
from itertools import chain

import bleach
import markdown
from django.shortcuts import get_object_or_404, render
import httpx
from rest_framework import generics, permissions, status, views
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from django.urls import reverse
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe

from blog.extractor import extract_article_from_url
from blog.models import Post, Article
from blog.serializers import ArticleAutoCreateSerializer, ArticleSerializer


def _markdown_to_html(markdown_text):
    """
    Converts Markdown text to HTML and sanitizes it.
    """
    html = markdown.markdown(markdown_text, extensions=["fenced_code", "codehilite"])
    # Define allowed tags and attributes for sanitization
    allowed_tags = [
        "a",
        "abbr",
        "acronym",
        "b",
        "blockquote",
        "code",
        "em",
        "i",
        "li",
        "ol",
        "p",
        "strong",
        "ul",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "pre",
        "div",
        "span",
        "br",
    ]
    allowed_attrs = {
        "*": ["id", "class"],
        "a": ["href", "title"],
        "abbr": ["title"],
        "acronym": ["title"],
    }
    sanitized_html = bleach.clean(
        html, tags=allowed_tags, attributes=allowed_attrs, strip=True
    )
    return mark_safe(sanitized_html)


def blog_list(request):
    posts = Post.objects.filter(status=1).order_by("-created_at")
    for post in posts:
        # Convert Markdown to HTML, then strip HTML tags for plain text preview
        post.plain_text_preview = strip_tags(_markdown_to_html(post.text))
    context = {
        "posts": posts,
    }
    return render(request, "blog/base.html", context)


def blog_category(request, category):
    posts = Post.objects.filter(categories__name__contains=category, status=1).order_by(
        "-created_at"
    )
    for post in posts:
        # Convert Markdown to HTML, then strip HTML tags for plain text preview
        post.plain_text_preview = strip_tags(_markdown_to_html(post.text))
    context = {
        "category": category,
        "posts": posts,
    }
    return render(request, "blog/base.html", context)


def blog_post(request, slug):
    post = get_object_or_404(Post, slug=slug)
    post.html_text = _markdown_to_html(post.text)  # Convert Markdown to HTML

    # Find related posts using semantic search (excluding the current post)
    related_posts = []
    if post.embedding is not None:
        from pgvector.django import CosineDistance

        related_posts = (
            Post.objects.filter(status=1)
            .exclude(pk=post.pk)
            .alias(distance=CosineDistance("embedding", post.embedding))
            .order_by("distance")[:3]
        )

    context = {
        "post": post,
        "related_posts": related_posts,
    }
    return render(request, "blog/post.html", context)


def blog_article(request):
    articles = Article.objects.order_by("-created_at")
    context = {
        "articles": articles,
    }
    return render(request, "blog/article.html", context)


def search_results(request):
    query = request.GET.get("q")
    processed_results = []
    if query:
        # Full-text search cosine distance + literal
        post_results = Post.objects.search(query, status=1)
        article_results = Article.objects.search(query)

        combined_results = sorted(
            chain(post_results, article_results),
            key=lambda instance: instance.created_at,
            reverse=True,
        )

        for result in combined_results:
            if isinstance(result, Post):
                text_content = result.text
                url = reverse("blog_post", args=[result.slug])
                is_external = False
                categories = result.categories.all()
                item_type = "Post"
            elif isinstance(result, Article):
                text_content = result.comment
                url = result.link
                is_external = True
                categories = None
                item_type = "Article"
            else:
                continue

            # Convert markdown to HTML for display in search results snippet if it's a Post
            if isinstance(result, Post):
                display_text_content = _markdown_to_html(text_content)
            else:
                display_text_content = text_content

            text = strip_tags(
                display_text_content
            )  # Strip tags from the HTML for snippet generation
            position = text.lower().find(query.lower())
            snippet = ""
            if position != -1:
                start = max(0, position - 50)
                end = min(len(text), position + len(query) + 50)
                raw_snippet = text[start:end]
                highlighted_snippet = re.sub(
                    f"({re.escape(query)})",
                    r'<mark class="p-0 bg-warning">\1</mark>',
                    raw_snippet,
                    flags=re.IGNORECASE,
                )
                snippet = mark_safe(f"...{highlighted_snippet}...")

            processed_results.append(
                {
                    "type": item_type,
                    "title": result.title,
                    "url": url,
                    "date": result.created_at,
                    "snippet": snippet,
                    "is_external": is_external,
                    "categories": categories,
                    "text": display_text_content,  # Pass the HTML text to the context
                }
            )

    context = {
        "query": query,
        "results": processed_results,
    }
    return render(request, "blog/search_results.html", context)


class ArticleListCreateAPIView(generics.ListCreateAPIView):
    """
    API endpoint that allows articles to be viewed or created.

    **GET:**
    Returns a list of all existing articles.
    No authentication is required for this method.

    **POST:**
    Creates a new article.
    Authentication is required for this method.

    *Request body:*
    ```json
    {
        "title": "string",
        "author": "string",
        "comment": "string",
        "link": "string (URL)"
    }
    ```
    """

    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class ArticleAutoCreateAPIView(views.APIView):
    """
    API endpoint that automatically creates an article from a URL.
    Extracts title, author, and description using Pydantic AI.

    **POST:**
    Creates a new article from a given URL.
    Authentication is required for this method.

    *Request body:*
    ```json
    {
        "url": "https://example.com/some-article",
        "comment": "optional comment override"
    }
    ```
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = ArticleAutoCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        url = serializer.validated_data["url"]
        user_comment = serializer.validated_data.get("comment", "").strip()

        try:
            extracted = extract_article_from_url(url)
        except httpx.HTTPStatusError as e:
            return Response(
                {"error": f"Failed to fetch URL: HTTP {e.response.status_code}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except httpx.RequestError as e:
            return Response(
                {"error": f"Failed to connect to URL: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {"error": f"Extraction failed: {str(e)}"},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        comment = user_comment if user_comment else extracted.description
        article = Article.objects.create(
            title=extracted.title[:200],
            author=extracted.author[:200],
            comment=comment,
            link=url,
        )

        response_serializer = ArticleSerializer(article)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
