### BASED ON: https://dev.to/levelupkoodarit/deploying-containerized-nginx-to-heroku-how-hard-can-it-be-3g14
### BASED ON: https://typeofnan.dev/how-to-serve-a-react-app-with-nginx-in-docker/

# BASED ON: https://docs.docker.com/samples/django/

FROM python:3.8-slim

# define working directory
# WORKDIR /app

# set environment variables to prevent .pyc and buffering outputs
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install application dependencies
# COPY requirements_docker.txt /app/requirements.txt
COPY requirements_docker.txt requirements.txt

# Adds apps for compiling
RUN apt-get update && \
    apt-get install libpq-dev gcc g++ --yes -q
#     apt-get install dialog apt-utils --yes && \

# add and run as non-root user
## RUN adduser --disabled-password myuser
## USER myuser

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
