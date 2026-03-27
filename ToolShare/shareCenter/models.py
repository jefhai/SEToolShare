from django.db import models
from django import forms
from django.core.validators import RegexValidator
from django.contrib.auth.models import User
from localflavor.us.us_states import STATE_CHOICES
from messageCenter.models import Reservation
from datetime import date

ZIPCODE_VALIDATOR = RegexValidator(regex=r'^\d{5}$', message='Zip code must be exactly 5 digits.')

# Creates a new user profile
class UserProfile(models.Model):
    """Custom User"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    zipCode = models.CharField(max_length=5, validators=[ZIPCODE_VALIDATOR])
    sAddress = models.CharField(max_length=30)
    city = models.CharField(max_length=30)
    state = models.CharField(max_length=30)
    timesLent = models.IntegerField()
    timesBorrowed = models.IntegerField()
    
    @classmethod
    def create(cls, user, zipCode, streetAddress, state, city):
        zipCode = str(zipCode).strip().zfill(5)
        profile = cls(user=user, zipCode=zipCode, sAddress=streetAddress, state=state, city=city, 
                      timesLent=0, timesBorrowed=0)
        return profile
    
    def numTools(self):
        numTools = len(ToolModel.objects.filter(owner=self))
        return numTools
    
    def hasShed(self):
        sheds = CommunityShed.objects.filter(owner=self)
        if len(sheds) > 0:
            return True
        else:
            return False 
    
class EditUserInfoForm(forms.Form):
    """Editing User Information"""
    error_css_class = 'alert alert-danger'
    firstName = forms.CharField(label='First Name:', widget=forms.TextInput(attrs={'class':'form-control'}))
    lastName = forms.CharField(label='Last Name:', widget=forms.TextInput(attrs={'class':'form-control'}))
    streetAddress = forms.CharField(label='Street Address', widget=forms.TextInput(attrs={'class':'form-control'}))
    city = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}))
    state = forms.CharField(widget=forms.Select(choices=STATE_CHOICES, attrs={'class':'form-control'}))
    zipcode = forms.CharField(
        max_length=5,
        min_length=5,
        validators=[ZIPCODE_VALIDATOR],
        widget=forms.TextInput(attrs={
            'maxlength': 5,
            'class': 'form-control red-tooltip',
            'rel': 'tooltip',
            'title': 'Warning! Changing ZipCode will delete your shed and take your tools out of sheds. ',
            'data-placement': 'left',
            'pattern': '\\d{5}',
            'inputmode': 'numeric',
        }),
    )
    email = forms.EmailField(widget=forms.TextInput(attrs={'class':'form-control'}))

class EditPassword(forms.Form):
    """Editing Password"""
    oldPassword = forms.CharField(label='Current Password', widget=forms.PasswordInput(attrs={'class':'form-control'}))
    password = forms.CharField(label='New Password',widget=forms.PasswordInput(attrs={'class':'form-control'}))
    confirmPassword = forms.CharField(label='Confirm New Password', widget=forms.PasswordInput(attrs={'class':'form-control'}))
    
    def __init__(self, user, data=None):
        self.user = user
        super(EditPassword, self).__init__(data=data)
        
    # If passwords do not match
    def clean(self):
        oldPassword = self.cleaned_data.get('oldPassword')
        password = self.cleaned_data.get('password')
        confirmPassword = self.cleaned_data.get('confirmPassword')
        if (self.user or self.user.is_active) and not self.user.check_password(oldPassword):
            raise forms.ValidationError("Current Password is incorrect.")
        if password and password != confirmPassword:
            raise forms.ValidationError("New passwords do not match")

        return self.cleaned_data
    
# Creates a new tool form      
class ToolModel(models.Model):
    #Model for a tool object
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=250)
    owner = models.ForeignKey('UserProfile', on_delete=models.CASCADE)
    pickupInformation = models.CharField(max_length=100)
    available = models.BooleanField()
    timesUsed = models.IntegerField()
    location = models.ForeignKey('CommunityShed', null=True, on_delete=models.SET_NULL)
    
    @classmethod
    def create(cls, owner, name, description, pickupInformation, location, available):
        newTool = cls(owner=owner, name=name, description=description, 
                      pickupInformation=pickupInformation, location=location, available=available,
                      timesUsed=0)
        return newTool
    
    def inShed(self):
        
        if self.location == None:
            return False
        return True

    def isReserved(self):
        for r in Reservation.objects.filter(tool_id=self.id):
            if r.startDate <= date.today() and r.endDate > date.today():
                return True
        return False
    
   
# Creates a new add tool form 
class AddToolForm(forms.Form):
    
    possibleLocations = [(0,'Home')]
    
    
    error_css_class = 'alert alert-danger'
    name = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'class':'form-control', 'size': 20}))
    description = forms.CharField(max_length=250, widget=forms.Textarea(attrs={'class':'form-control', 'style': 'resize: none' }))
    pickup_info = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class':'form-control' }))
    location = forms.IntegerField(widget=forms.Select(choices=possibleLocations,attrs={'class':'form-control' }))
    available = forms.BooleanField(initial=True, required=False )
    def __init__(self, choices, *args, **kwargs):
       super(AddToolForm, self).__init__(*args, **kwargs)
       self.fields["location"] = forms.IntegerField(widget=forms.Select(choices=choices,attrs={'class':'form-control' }))
    
    
    def clean(self):
        name = self.cleaned_data.get('name')
        description = self.cleaned_data.get('description')
        pickup_info = self.cleaned_data.get('pickup_info')
        location = self.cleaned_data.get('location')
        if name and len(name) > 30:
            raise forms.ValidationError("Name is too long")
        elif description and len(description) > 250:
            raise forms.ValidationError("Description is too long")
        elif pickup_info and len(pickup_info) > 100:
            raise forms.ValidationError("Pickup Information is too long")
        return self.cleaned_data
    
class EditToolForm(forms.Form):
    
    possibleLocations = [(0,'Home')]
    
    error_css_class = 'alert alert-danger'
    name = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'class':'form-control', 'size': 20}))
    description = forms.CharField(widget=forms.Textarea(attrs={'class':'form-control', 'style': 'resize: none' }))
    pickup_info = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control' }))
    location = forms.IntegerField(widget=forms.Select(choices=possibleLocations,attrs={'class':'form-control' }))
    available = forms.BooleanField(initial=True, required=False)
    
    def __init__(self, choices, *args, **kwargs):
       super(EditToolForm, self).__init__(*args, **kwargs)
       self.fields["location"] = forms.IntegerField(widget=forms.Select(choices=choices,attrs={'class':'form-control' }))
       
    def clean(self):
        name = self.cleaned_data.get('name')
        description = self.cleaned_data.get('description')
        pickup_info = self.cleaned_data.get('pickup_info')
        location = self.cleaned_data.get('location')
        if name and len(name) > 30:
            raise forms.ValidationError("Name is too long!")
        elif description and len(description) > 250:
            raise forms.ValidationError("Description is too long!")
        elif pickup_info and len(pickup_info) > 100:
            raise forms.ValidationError("Pickup Information is too long!")
        return self.cleaned_data
    
class AddCommunityShedForm(forms.Form):
    error_css_class = 'alert alert-danger'
    address = forms.CharField(max_length=30, label='Address', widget=forms.TextInput(attrs={'class':'form-control'}))
    city = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'class':'form-control'}))
    
    
    def clean(self):
        address = self.cleaned_data.get('address')
        city = self.cleaned_data.get('city')
        return self.cleaned_data

    
class CommunityShed(models.Model):
    owner = models.ForeignKey('UserProfile', on_delete=models.CASCADE)
    address = models.CharField(max_length=30)
    city = models.CharField(max_length=30)
    zipcode = models.CharField(max_length=5, validators=[ZIPCODE_VALIDATOR])

    @classmethod
    def create(cls, owner, address, city, zipcode):
        zipcode = str(zipcode).strip().zfill(5)
        newShed = cls(owner=owner, address=address, city=city, zipcode=zipcode)
        return newShed
    

class ToolSearchForm(forms.Form):
    error_css_class = 'alert alert-danger'

    #,('AV','Availability')
    filters = [('DA','Date Added'),('NA','Name'),('OW','Owner')]
    possibleLocations = [(-1,'All'),(0,'Home')]
    
    
    searchTerms = forms.CharField(max_length=180, required=False, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Search'}))
    filter = forms.CharField(widget=forms.Select(choices=filters,attrs={'class':'form-control', 'placeholder':'Filter' }))
    location = forms.IntegerField(widget=forms.Select(choices=possibleLocations,attrs={'class':'form-control' }))
    
    def __init__(self, possibleLocations, *args, **kwargs):
       super(ToolSearchForm, self).__init__(*args, **kwargs)
       self.fields["location"] = forms.IntegerField(widget=forms.Select(choices=possibleLocations,attrs={'class':'form-control' }))
    
    def clean(self):
        searchTerms = self.cleaned_data.get('searchTerms')
        filter = self.cleaned_data.get('filter')
        location = self.cleaned_data.get('location')
        return self.cleaned_data



    
