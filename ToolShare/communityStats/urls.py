from django.urls import re_path
from communityStats import views

app_name = 'communityStats'

urlpatterns = [
    re_path(r'^stats/?$', views.statReport, name='stats'),
]
