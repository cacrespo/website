import re

from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe

from blog.models import Post, Article


def blog_list(request):
    posts = Post.objects.all().order_by("-created_at")
    context = {
        "posts": posts,
    }
    return render(request, "blog/base.html", context)


def blog_category(request, category):
    posts = Post.objects.filter(categories__name__contains=category).order_by(
        "-created_at"
    )
    context = {
        "category": category,
        "posts": posts,
    }
    return render(request, "blog/base.html", context)


def blog_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    context = {
        "post": post,
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
    if query:
        results = Post.objects.filter(
            Q(title__icontains=query) | Q(text__icontains=query)
        ).order_by("-created_at")
        for post in results:
            text = strip_tags(post.text)
            # Find the position of the query in the text
            position = text.lower().find(query.lower())
            if position != -1:
                # Create a snippet around the query
                start = max(0, position - 50)
                end = min(len(text), position + len(query) + 50)
                snippet = text[start:end]
                # Highlight the query in the snippet, case-insensitively
                highlighted_snippet = re.sub(
                    f"({re.escape(query)})",
                    r'<mark class="p-0 bg-warning">\1</mark>',
                    snippet,
                    flags=re.IGNORECASE,
                )
                post.snippet = mark_safe(f"...{highlighted_snippet}...")
    else:
        results = Post.objects.none()

    context = {
        "query": query,
        "posts": results,
    }
    return render(request, "blog/search_results.html", context)
