from django.urls import path
from . import views

urlpatterns = [
    path("", views.blog_list, name="blog_list"),
    path("post/<int:pk>/", views.blog_post, name="blog_post"),
    path("category/<category>/", views.blog_category, name="blog_category"),
    path("articles/", views.blog_article, name="blog_article"),
    path("search/", views.search_results, name="search_results"),
]
