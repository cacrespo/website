import os
from .base import *  # noqa

import logfire

ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "").split(",")

logfire.configure()
logfire.instrument_django()
