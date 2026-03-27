from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.template import RequestContext, loader
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth import login, logout
from login.models import loginForm
from shareCenter.models import ToolModel, UserProfile
from messageCenter.models import Reservation

# Logout user method 
def logoutUser(request):
    logout(request)
    return HttpResponseRedirect('/login/')  # Redirect to a success page.

# Login user method
def loginUser(request):
    # Checks if user is already logged in
    if request.user.is_authenticated:
        return HttpResponseRedirect("/tooldirectory/")  # Redirect to a tool directory page.
    form = loginForm(request.POST or None)
    # Logs in user and sends user to a page redirect
    if request.POST and form.is_valid():
        user = form.login(request)
        if user:
            login(request, user)
            return HttpResponseRedirect("/tooldirectory/")  # Redirect to a success page.
    return render(request, 'login/login.html', {'form': form})

# Home Page method
def home(request):
	shareZones = UserProfile.objects.values('zipCode').distinct()
	bubbleCharArrayData = [["ShareZone", 'Reservations', 'Tool', 'Users']]
	for sz in shareZones:
		print(sz['zipCode'])
		bubbleCharArrayData.append([str(sz['zipCode']).zfill(5), len(Reservation.objects.filter(tool__owner__zipCode=sz['zipCode'])),len(ToolModel.objects.filter(owner__zipCode=sz['zipCode'])), len(UserProfile.objects.filter(zipCode=sz['zipCode']))]
		)
	bubbleData=str(bubbleCharArrayData)

	return render(request, 'login/home.html', {'bubbleCharArrayData': bubbleData})

# Credits page method
def credits(request):

    return render(request, 'login/credits.html')#, {'form': form})
    
