### BASED ON: https://docs.docker.com/samples/django/
### BASED ON: https://testdriven.io/blog/deploying-django-to-heroku-with-docker/

FROM python:3.8-slim

# define working directory

# set environment variables to prevent .pyc and buffering outputs
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install application dependencies
COPY requirements_docker.txt requirements.txt

# Adds apps for compiling
RUN apt-get update && \
    apt-get install libpq-dev gcc g++ --yes -q

# Creates virtual environment 
RUN python -m venv --system-site-packages the_env && \
    . the_env/bin/activate && \
    pip install --upgrade pip  && \
    pip install wheel && \
    pip install -r requirements.txt

# Add app
COPY . .

# run gunicorn
CMD . the_env/bin/activate && \
    gunicorn api_rest.wsgi:application --bind 0.0.0.0:$PORT
