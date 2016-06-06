from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.home),
    url(r'^home.html/?$', views.home),
    url(r'^indexURL.html/?$', views.indexURL),
    url(r'^search/?$', views.search),
]
