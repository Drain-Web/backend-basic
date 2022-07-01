from django.urls import re_path, path

from protobufs_server import views as ptbf_views

urlpatterns = [
    re_path(r'protobuf_server/(?P<product_id>.*)/(?P<zoom>.*)/(?P<x>.*)/(?P<y>.*)', ptbf_views.open_file)
]

# path(r'v1dw/locations', crud_views.locations_with_filters),