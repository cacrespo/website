from blog import views as blog_views
from django.conf import settings
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("pages.urls")),
    path("blog/", include("blog.urls")),
    path("articles/", blog_views.blog_article, name="blog_article"),
    path("api/v1/", include("blog.api_urls")),
]

if settings.DEBUG:
    from debug_toolbar.toolbar import debug_toolbar_urls  # type: ignore # noqa

    urlpatterns += debug_toolbar_urls()
