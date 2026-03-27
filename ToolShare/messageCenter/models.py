from django.db import models
from django import forms
from django.contrib.auth.models import User
from datetime import datetime

class AlertMessage(models.Model):
    
    sender = models.ForeignKey('shareCenter.UserProfile', related_name='alertmessage_sender', on_delete=models.CASCADE)
    receiver = models.ForeignKey('shareCenter.UserProfile', related_name='alertmessage_receiver', on_delete=models.CASCADE)
    subject = models.CharField(max_length=140)
    content = models.CharField(max_length=500)
    read = models.BooleanField()
    isRequest = models.BooleanField()
    senderUsername = models.CharField(max_length=50)
    toolId = models.IntegerField(null=True)
    startDate = models.DateField(null=True)
    endDate = models.DateField(null=True)
    
    @classmethod
    def create(cls, sender, receiver, subject, content, isRequest, toolId=None, startDate=None, endDate=None ):
        alertMessage = cls(sender=sender, receiver=receiver, subject=subject, content=content,isRequest=isRequest, 
                           read=False, toolId=toolId, senderUsername=(User.objects.get(id=sender.user_id).username), startDate=startDate, endDate=endDate)
        return alertMessage
    
    
class SendMessageForm(forms.Form):
    error_css_class = 'alert alert-danger'
    content = forms.CharField(label="", widget=forms.Textarea(attrs={'class':'form-control', 'style': 'resize: none', 'placeholder':'Message Content'}))
    
    def clean(self):
        content = self.cleaned_data.get('content')
        if content == None or len(content) > 500:
            raise forms.ValidationError("content is too long!")
        return self.cleaned_data
    
class MakeRequest(forms.Form):
    error_css_class = 'alert alert-danger'
    startDate = forms.DateField(label="Start Date", widget=forms.TextInput( attrs={ 'readonly':'readonly', 'cursor':'allowed', 'class':'form-control', 'data-provide': 'datepicker', 'data-date-autoclose': 'true',
                                                                                    'data-date-start-date': str(datetime.day) + '-' + str(datetime.month) + '-' + str(datetime.year)  }))
    endDate = forms.DateField(label="End Date", widget=forms.TextInput( attrs={ 'readonly':'readonly', 'class':'form-control', 'data-provide': 'datepicker', 'data-date-autoclose': 'true',
                                                                                'data-date-start-date': str(datetime.day) + '-' + str(datetime.month) + '-' + str(datetime.year)   }))
    message = forms.CharField(required=False, label="", widget=forms.Textarea(attrs={'class':'form-control', 'style': 'resize: none', 'placeholder':'Optional Message'}))
    
    def clean(self):
        startDate = self.cleaned_data.get('startDate')
        endDate = self.cleaned_data.get('endDate')
        message = self.cleaned_data.get('message')
        if message == len(message) > 500:
            raise forms.ValidationError("content is too long!")
        if endDate < startDate:
            raise forms.ValidationError("Invalid Dates")
        return self.cleaned_data
    
class Reservation(models.Model):
    tool = models.ForeignKey('shareCenter.ToolModel', on_delete=models.CASCADE)
    borrower = models.ForeignKey('shareCenter.UserProfile', on_delete=models.CASCADE)
    startDate = models.DateField()
    endDate = models.DateField()
    
    @classmethod
    def create(cls, tool, borrower, startDate, endDate):
        newReservation = cls(tool=tool, borrower=borrower, startDate=startDate, endDate=endDate)
        
        return newReservation



"""
class DenyRequest(forms.Form):
    error_css_class = 'alert alert-danger'
    content = forms.CharField(widget=forms.Textarea(attrs={'class':'form-control' }))

class MsgReply(forms.Form):
    error_css_class = 'alert alert-danger'
    content = forms.CharField(widget=forms.Textarea(attrs={'class':'form-control' }))
"""
