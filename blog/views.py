import re
from itertools import chain

from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
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
    processed_results = []
    if query:
        post_results = Post.objects.filter(
            Q(title__icontains=query) | Q(text__icontains=query)
        )
        article_results = Article.objects.filter(
            Q(title__icontains=query) | Q(comment__icontains=query)
        )

        combined_results = sorted(
            chain(post_results, article_results),
            key=lambda instance: instance.created_at,
            reverse=True,
        )

        for result in combined_results:
            if isinstance(result, Post):
                text_content = result.text
                url = reverse("blog_post", args=[result.pk])
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

            text = strip_tags(text_content)
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
                    "text": text_content,
                }
            )

    context = {
        "query": query,
        "results": processed_results,
    }
    return render(request, "blog/search_results.html", context)
