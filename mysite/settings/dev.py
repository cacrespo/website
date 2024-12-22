from .base import *

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

ALLOWED_HOSTS = ['localhost', '0.0.0.0', '127.0.0.1']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

SECRET_KEY = "foo"

DEBUG = True
