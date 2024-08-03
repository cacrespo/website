# pull official base image
FROM python:3.10

# set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# set work directory
WORKDIR /usr/src/app

# install dependencies
COPY ./requirements.txt .
COPY ./requirements-dev.txt .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install -r requirements-dev.txt

# copy project
COPY . .
