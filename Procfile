release: python manage.py migrate
web: gunicorn api_rest.wsgi --timeout 60 --graceful_timeout 60
