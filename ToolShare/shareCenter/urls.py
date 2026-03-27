from django.urls import re_path
from shareCenter import views

app_name = 'shareCenter'

urlpatterns = [
    re_path(r'^addtool/?$', views.addTool, name='addtool'),
    re_path(r'^userdirectory/?$', views.userDirectory, name='userdirectory'),
    re_path(r'^tool/(?P<tool_id>\d+)/?$', views.toolInfo, name='tool'),
    re_path(r'^user/(?P<username>\w+)/?$', views.userProfile, name='username'),
    re_path(r'^tool/delete/(?P<tool_id>\d+)/?$', views.deleteTool, name='deletetool'),
    re_path(r'^tool/edit/(?P<tool_id>\d+)/?$', views.editTool, name='edittool'),
    re_path(r'^tool/changestate/(?P<tool_id>\d+)/?$', views.changeToolState, name='changeToolState'),
    re_path(r'^edituser/(?P<username>\w+)/?$', views.editUserInfo, name='edituserinfo'),
    re_path(r'^editpassword/?$', views.editPassword, name='editpassword'),
    re_path(r'^createshed/?$', views.createShed, name='createshed'),
    re_path(r'^shed/(?P<username>\w+)/?$', views.shed, name='shed'),
    re_path(r'^shedlist/?$', views.shedList, name='shedlist'),
    re_path(r'^deleteshed/?$', views.deleteShed, name='deleteshed'),
]
