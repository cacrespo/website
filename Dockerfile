# pull official base image
FROM python:3.10 AS base

# set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=mysite.settings.base

# set work directory
WORKDIR /usr/src/app

# install dependencies
COPY ./requirements.txt .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# copy project
COPY . .

RUN python manage.py collectstatic --no-input

FROM base AS development
ENV DJANGO_SETTINGS_MODULE=mysite.settings.dev

COPY ./requirements-dev.txt .
RUN pip install -r requirements-dev.txt

CMD ["python", "manage.py", "runserver", "0.0.0.0:80"]

FROM base AS production
ENV DJANGO_SETTINGS_MODULE=mysite.settings.prod

# Command to run Gunicorn
CMD ["sh", "-c", "gunicorn mysite.wsgi:application --bind 0.0.0.0:80"]
