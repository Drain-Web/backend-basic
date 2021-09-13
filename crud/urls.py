from django.urls import re_path, path

from crud import views

urlpatterns = [

    re_path(r'^v1/filter/(?P<filter_id>.*)$', views.filter_detail),
    path(r'v1/filters', views.filter_list),
    path(r'v1/locations', views.location),
    path(r'v1/parameters/', views.list_parameters),
    path(r'v1/region', views.region),
    path(r'v1/timeseries/', views.timeseries_list_by_querystring),
    path(r'v1dw/locations', views.locations_dynamic),
    path(r'v1dw/threshold_groups', views.threshold_groups_list),
    path(r'v1dw/threshold_value_sets', views.threshold_value_sets_list),
    path(r'v1dw/boundaries', views.bondary_list),
    path(r'v1dw/filters/', views.filter_list_by_querystring),
    path(r'v1dw/maps/', views.maps_list),
    path(r'v1dw/parameter_groups/', views.list_parameter_groups),
    path(r'v1dw/module_instances', views.module_instances)
]

# path(r'v1dw/locations', views.locations_with_filters),