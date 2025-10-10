from .base import *  # noqa
from .base import INSTALLED_APPS, MIDDLEWARE
import os

ALLOWED_HOSTS = ["localhost", "0.0.0.0", "127.0.0.1"]

SECRET_KEY = "foo"

DEBUG = True

# INTERNAL_IPS is not used because Docker changes REMOTE_ADDR on each run.
# Instead, we directly configure SHOW_TOOLBAR_CALLBACK to determine when
# the toolbar should be shown.
#
# INTERNAL_IPS = ["localhost", "0.0.0.0", "127.0.0.1", "::1"]

# Only enable the toolbar when we're in debug mode and we're
# not running tests. Django will change DEBUG to be False for
# tests, so we can't rely on DEBUG alone.
TESTING = "TESTING" in os.environ

ENABLE_DEBUG_TOOLBAR = DEBUG and not TESTING
if ENABLE_DEBUG_TOOLBAR:
    INSTALLED_APPS += [
        "debug_toolbar",
    ]
    MIDDLEWARE += [
        "debug_toolbar.middleware.DebugToolbarMiddleware",
    ]

    DEBUG_TOOLBAR_CONFIG = {"SHOW_TOOLBAR_CALLBACK": lambda request: DEBUG}

# Print emails to console in development
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
