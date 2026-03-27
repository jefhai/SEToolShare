from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.template import RequestContext, loader
from django.http import HttpResponseRedirect
from django.shortcuts import render
from shareCenter.models import UserProfile
from django.contrib.auth.models import User
from registration.models import RegistrationForm

# Register user method
def register(request):
    if request.user.is_authenticated:
        
        return HttpResponseRedirect('/tooldirectory/') 
    if request.method == 'POST': 					# If the form has been submitted...
        form = RegistrationForm(request.POST) 		# A form bound to the POST data
        if form.is_valid(): 						# All validation rules pass
            fName = form.cleaned_data['firstName']
            lName = form.cleaned_data['lastName'] 
            username = form.cleaned_data['username']
            pwd = form.cleaned_data['password']
            email = form.cleaned_data['email']
            sAddress = form.cleaned_data['streetAddress']
            city = form.cleaned_data['city']
            state = form.cleaned_data['state']
            zcode = form.cleaned_data['zipcode']     

            # Tries to create a new user and add them to the database
            try:
                u = User.objects.create_user(username, email=email, password=pwd, first_name=fName, last_name=lName)
                UserProfile.create(u,zcode,sAddress,state,city).save()  # Saves new user to database
            except:
                #Add error
                return HttpResponseRedirect('#ERROR') 
            return HttpResponseRedirect('/login/') 	# Redirect after POST
    else:
        form = RegistrationForm() 					# An unbound form

    return render(request, 'registration/register.html', {'form': form})
    
    
