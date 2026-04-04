from django.urls import re_path
from login import views

app_name = 'login'

urlpatterns = [
    re_path(r'^$', views.loginUser, name='login'),
    re_path(r'^demo/?$', views.startDemo, name='demo'),
    re_path(r'^home/?$', views.home, name='home'),
    re_path(r'^credits/?$', views.credits, name='credits'),
]
