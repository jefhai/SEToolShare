from django.urls import re_path
from messageCenter import views

app_name = 'messageCenter'

urlpatterns = [
    re_path(r'^$', views.inboxView, name='messageCenter'),
    re_path(r'^sendMessage/(?P<user_id>\d+)/?$', views.sendMessage, name='sendMessage'),
    re_path(r'^message/(?P<message_id>\d+)/?$', views.messageView, name='viewMessage'),
    re_path(r'^delete/(?P<message_id>\d+)/?$', views.deleteMessage, name='deleteMessage'),
    re_path(r'^sendrequest/(?P<toolId>\d+)/?$', views.sendToolRequest, name='sendRequest'),
    re_path(r'^approverequest/(?P<message_id>\d+)/(?P<toolId>\d+)/?$', views.approveRequest, name='approveRequest'),
    re_path(r'^reservations/delete/(?P<reservation_id>\d+)/?$', views.deleteReservation, name='deleteReservation'),
    re_path(r'^reservations/return/(?P<reservation_id>\d+)/?$', views.returnReservation, name='returnReservation'),
    re_path(r'^reservations/?$', views.myReservations, name='myreservations'),
]
