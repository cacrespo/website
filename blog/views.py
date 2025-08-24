from django.shortcuts import render, get_object_or_404
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
