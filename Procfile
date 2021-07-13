release: python manage.py migrate
web: gunicorn api_rest.wsgi
gunicorn api_rest.wsgi --timeout 60
gunicorn api_rest.wsgi --graceful_timeout 60
