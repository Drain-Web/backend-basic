from django.urls import re_path, path

from crud import views

urlpatterns = [ 
    re_path(r'^v1/region$', views.region),
    re_path(r'^v1/locations$', views.location),
    re_path(r'^v1/filters$', views.filter_list),
    re_path(r'^v1/filter/(?P<filter_id>.*)$', views.filter_detail),
    path(r'v1/timeseries/', views.timeseries_list_by_querystring),
    path(r'v1/parameters/', views.list_parameters)
]
