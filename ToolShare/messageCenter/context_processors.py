from django.template import RequestContext, loader
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.conf import settings
from django.contrib.auth.models import User
from messageCenter.models import AlertMessage, SendMessageForm
from shareCenter.models import UserProfile, ToolModel

def numUnread(request):
    if request.user.is_authenticated and not request.user.is_staff:
        currentUser = UserProfile.objects.get(user_id=request.user.id)
        msgAmount = len(AlertMessage.objects.filter(receiver_id=currentUser.id, ).filter(read=False))
        hasShed = currentUser.hasShed()
    else:
        hasShed = False
        msgAmount=0
    return {
        'msgAmount' : msgAmount, 'userHasShed' : hasShed,
        'message_max_length': getattr(settings, 'MESSAGE_MAX_LENGTH', 1000),
    }
