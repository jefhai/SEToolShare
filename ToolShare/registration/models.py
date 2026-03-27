from django.db import models
from django import forms
from django.core.validators import RegexValidator
from localflavor.us.us_states import STATE_CHOICES

# Creates a new registration form 
class RegistrationForm(forms.Form):
    
    error_css_class = 'alert alert-danger'
    firstName = forms.CharField(max_length=50, label='First Name:', widget=forms.TextInput(attrs={'class':'form-control'}))
    lastName = forms.CharField(max_length=50, label='Last Name:', widget=forms.TextInput(attrs={'class':'form-control'}))
    streetAddress = forms.CharField(max_length=30, label='Street Address', widget=forms.TextInput(attrs={'class':'form-control'}))
    city = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'class':'form-control'}))
    state = forms.CharField(max_length=20, widget=forms.Select(choices=STATE_CHOICES, attrs={'class':'form-control'}))
    zipcode = forms.CharField(
        max_length=5,
        min_length=5,
        validators=[RegexValidator(regex=r'^\d{5}$', message='Zip code must be exactly 5 digits.')],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'maxlength': '5',
            'minlength': '5',
            'pattern': '\\d{5}',
            'inputmode': 'numeric',
            'title': 'Zip code must be exactly 5 digits.',
        }),
    )
    email = forms.EmailField(widget=forms.TextInput(attrs={'class':'form-control'}))
    username = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'class':'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control'}))
    confirmPassword = forms.CharField(label='Confirm Password', widget=forms.PasswordInput(attrs={'class':'form-control'}))
    
    # If passwords do not match
    def clean(self):
        password = self.cleaned_data.get('password')
        confirmPassword = self.cleaned_data.get('confirmPassword')

        if password and password != confirmPassword:
            raise forms.ValidationError("Passwords don't match")

        return self.cleaned_data
