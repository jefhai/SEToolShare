from django.db import models
from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.models import User

# Creates a new login form 
class loginForm(forms.Form):
    error_css_class = 'alert alert-danger'
    username = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'class':'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control'}))
	
    # Redefines the clean method to include error raising
    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        if (not user or not user.is_active) and username != None and password != None:
            raise forms.ValidationError("Sorry, that login was invalid. Please try again.")
        return self.cleaned_data

    # Redefines the login method
    def login(self, request):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        return user


class DemoUserScope(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    scope = models.CharField(max_length=20)
    role = models.CharField(max_length=10)
