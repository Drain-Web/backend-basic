from django.urls import re_path

from netflow_server import views as ntfl_views

urlpatterns = [
    re_path(r'netflow_server/(?P<netflow_id>.*)', ntfl_views.open_file)
]

# path(r'v1dw/locations', crud_views.locations_with_filters),