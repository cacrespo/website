import time
from django.conf import settings
from django.contrib import messages
from django.core.cache import cache
from django.core.mail import send_mail
from django.http import FileResponse, HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.cache import cache_control
from django.views.decorators.http import require_GET

from blog.models import Activity

from .forms import ContactForm


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
    if request.method == "POST":
        ip_address = request.META.get("REMOTE_ADDR")
        cache_key = f"contact_form_{ip_address}"

        # Check if this IP has submitted in the last hour (production only)
        if not settings.DEBUG and cache.get(cache_key):
            messages.warning(
                request,
                "You have already submitted the form recently. Please try again later.",
            )
            return HttpResponseRedirect(reverse("contact"))

        form = ContactForm(request.POST)
        if form.is_valid():
            # Simulate email sending delay in development
            if settings.DEBUG:
                time.sleep(2)

            name = form.cleaned_data["name"]
            email = form.cleaned_data["email"]
            message = form.cleaned_data["message"]
            message_body = f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}"
            send_mail(
                f"Contact Form submission from {name}",
                message_body,
                email,  # From user's submitted email
                ["lvccrespo@gmail.com"],
            )
            messages.success(
                request, "Your message has been sent successfully! Thank you. ✨"
            )

            # Set cache for this IP for 1 hour (production only)
            if not settings.DEBUG:
                cache.set(cache_key, True, 3600)

            return HttpResponseRedirect(reverse("contact"))
    else:
        form = ContactForm()

    return render(request, "pages/contact.html", {"form": form})


# def about(request):
#    return render(request, "pages/about.html", {})
