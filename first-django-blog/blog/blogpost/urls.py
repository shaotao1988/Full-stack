from django.urls import path, include
from django.conf.urls import re_path
from . import views

urlpatterns = [
    re_path('^$', views.index),
    re_path('(?P<slug>[^\\.]+)', views.view_post, name = 'view_post')
]