import os
from .base import *  # noqa
from .base import INSTALLED_APPS, BASE_DIR, STORAGES

import logfire
import sentry_sdk

ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "").split(",")

csrf_trusted = os.environ.get(
    "DJANGO_CSRF_TRUSTED_ORIGINS",
    "https://cacrespo.xyz,https://www.cacrespo.xyz",
)
CSRF_TRUSTED_ORIGINS = [
    origin.strip() for origin in csrf_trusted.split(",") if origin.strip()
]

# Security Hardening
SECURE_SSL_REDIRECT = os.environ.get("SECURE_SSL_REDIRECT", "true").lower() == "true"
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = int(os.environ.get("SECURE_HSTS_SECONDS", 31536000))
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

INSTALLED_APPS += [
    "dbbackup",
]

# Production Email Settings
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.environ.get("EMAIL_HOST")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", 587))
EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", "true").lower() == "true"
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")

logfire.configure(send_to_logfire="if-token-present")
logfire.instrument_django()

sentry_sdk.init(
    dsn=os.environ.get("SENTRY_DSN"),
    send_default_pii=os.environ.get("SENTRY_SEND_DEFAULT_PII", "false").lower()
    == "true",
    traces_sample_rate=float(os.environ.get("SENTRY_TRACES_SAMPLE_RATE", "0.2")),
    _experiments={
        "continuous_profiling_auto_start": True,
    },
)

# DJANGO-DBBACKUP Settings
STORAGES["dbbackup"] = {
    "BACKEND": "django.core.files.storage.FileSystemStorage",
    "OPTIONS": {"location": BASE_DIR / "backups"},
}
