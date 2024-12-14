import os
from .base import *  # noqa

import dj_database_url


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "").split(",")

DATABASES = {
    'default': dj_database_url.config(
        conn_max_age=600,
        conn_health_checks=True,
    ),
}
