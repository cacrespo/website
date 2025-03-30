from django.conf import settings
from django.contrib import admin
from django.urls import include, path

from debug_toolbar.toolbar import debug_toolbar_urls

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("pages.urls")),
    path("blog/", include("blog.urls")),
]

if settings.DEBUG:
    import debug_toolbar  # type: ignore # noqa

    urlpatterns += debug_toolbar_urls()
