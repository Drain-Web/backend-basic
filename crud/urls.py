from django.conf.urls import url
from crud import views

urlpatterns = [ 
    url(r'^api/region$', views.region)
]
