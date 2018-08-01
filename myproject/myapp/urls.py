# -*- coding: utf-8 -*-
from django.conf.urls import url
from myproject.myapp.views import list
from myproject.myapp.views import filename


urlpatterns = [
    url(r'^list/$', list, name='list')
    url(r'^filename/$', filename, name='filename')
]
