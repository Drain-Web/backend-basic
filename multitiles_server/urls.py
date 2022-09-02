from django.urls import re_path

from multitiles_server import views as img_views

urlpatterns = [
    re_path(r'multitiles_server/(?P<product_id>.*)/(?P<zoom>.*)/(?P<x>.*)/(?P<y>.*)', img_views.open_file)
]