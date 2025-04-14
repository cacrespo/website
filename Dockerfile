# pull official base image
FROM python:3.13 AS base

# For use docker-compose enviroment vars
ARG DATABASE_URL
ARG DJANGO_ALLOWED_HOSTS
ARG LOGFIRE_TOKEN

# set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
ENV DATABASE_URL=${DATABASE_URL}
ENV DJANGO_ALLOWED_HOSTS=${DJANGO_ALLOWED_HOSTS}
ENV DJANGO_SETTINGS_MODULE=mysite.settings.base
ENV LOGFIRE_TOKEN=${LOGFIRE_TOKEN}

# set work directory
WORKDIR /usr/src/app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# copy project
COPY . .
RUN uv sync --frozen

# ------------------------------
# Development Configuration
# ------------------------------
FROM base AS development
ENV DJANGO_SETTINGS_MODULE=mysite.settings.dev

RUN uv sync --all-groups

# Run the Django development server
CMD ["uv", "run", "manage.py", "runserver", "0.0.0.0:8000"]

# ------------------------------
# Production Configuration
# ------------------------------
FROM base AS production
ENV DJANGO_SETTINGS_MODULE=mysite.settings.prod

# Collect static files to be served in production
RUN python manage.py collectstatic --no-input

# Command to run Gunicorn
CMD ["sh", "-c", "gunicorn mysite.wsgi:application --bind 0.0.0.0:8000"]
