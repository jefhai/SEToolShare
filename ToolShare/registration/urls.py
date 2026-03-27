from django.urls import re_path
from registration import views

app_name = 'registration'

urlpatterns = [
    re_path(r'^$', views.register, name='registration'),
]
