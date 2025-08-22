from django.conf import settings
from django.http import FileResponse, HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.cache import cache_control
from django.views.decorators.http import require_GET

from blog.models import Activity


@require_GET
@cache_control(max_age=60 * 60 * 24, immutable=True, public=True)  # one day
def favicon(request: HttpRequest) -> HttpResponse:
    file = (settings.BASE_DIR / "static" / "img" / "favicon.png").open("rb")
    return FileResponse(file)


def home(request):
    activities = Activity.objects.order_by("-created_at")[:5]
    context = {
        "activities": activities,
    }
    return render(request, "pages/home.html", context)


def contact(request):
    return render(request, "pages/contact.html", {})


#def about(request):
#    return render(request, "pages/about.html", {})
