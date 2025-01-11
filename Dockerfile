# pull official base image
FROM python:3.13 AS base

# For use docker-compose enviroment vars
ARG DJANGO_ALLOWED_HOSTS

# set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_ALLOWED_HOSTS=${DJANGO_ALLOWED_HOSTS}
ENV DJANGO_SETTINGS_MODULE=mysite.settings.base

# set work directory
WORKDIR /usr/src/app

# install dependencies
COPY ./requirements.txt .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# copy project
COPY . .

# ------------------------------
# Development Configuration
# ------------------------------
FROM base AS development
ENV DJANGO_SETTINGS_MODULE=mysite.settings.dev

# Install the development dependencies
COPY ./requirements-dev.txt .
RUN pip install -r requirements-dev.txt

# Run the Django development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# ------------------------------
# Production Configuration
# ------------------------------
FROM base AS production
ENV DJANGO_SETTINGS_MODULE=mysite.settings.prod
ENV LOGFIRE_TOKEN=${LOGFIRE_TOKEN}

# Collect static files to be served in production
RUN python manage.py collectstatic --no-input

# Command to run Gunicorn
CMD ["sh", "-c", "gunicorn mysite.wsgi:application --bind 0.0.0.0:8000"]
