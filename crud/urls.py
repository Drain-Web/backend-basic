from django.conf.urls import url
from crud import views

urlpatterns = [ 
    url(r'^v1/region$', views.region),
    url(r'^v1/locations$', views.location),
    url(r'^v1/filters$', views.filter_list),
    url(r'^v1/filter/(?P<id>[0-9]+)$', views.filter_detail),
    url(r'^v1/timeseries$', views.timeseries_list)
]
