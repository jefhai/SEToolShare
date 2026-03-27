from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.template import RequestContext, loader
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from messageCenter.models import AlertMessage, SendMessageForm, MakeRequest, Reservation
from shareCenter.models import UserProfile, ToolModel, CommunityShed
from datetime import date
from django.contrib import messages




def messageView(request, message_id):
    """View for reading a message
    """


    if len(AlertMessage.objects.filter(id=message_id)) == 0:    # Check if requested message exists

        return HttpResponseRedirect('/messagecenter/')


    msg = AlertMessage.objects.get(id=message_id)   # gets the message to view
    doesConflict = False    # sets initial value of reservation conflict to false

    if not request.user.is_authenticated:   # Check if user is logged in properly
        return HttpResponseRedirect('/login/')  # If not, send them to the logib page


    

    if not msg.read:    # If message is unread
        msg.read = True
        msg.save()

    existingReservations = Reservation.objects.filter(tool_id=msg.toolId)

    if request.method == 'POST':    # If reply form was submitted

        currentUser = UserProfile.objects.get(user_id=request.user.id)
        content = None
        if msg.subject == "Request":    # Checks if message being viewed is a request


            for r in existingReservations:  # Check if request conflicts with existing reservation

                if not ((msg.startDate < r.startDate and msg.endDate < r.startDate) or
                        (msg.startDate >= r.endDate and msg.endDate > r.endDate)):
                    doesConflict = True

            form = SendMessageForm(request.POST)
            sub = "Request Declined"

            if form.is_valid():                     # All validation rules pass
                content = form.cleaned_data['content']
                content = User.objects.get(id=currentUser.user_id).username + \
                    " Has denied your request because: " + content


        else:   # Message is not a request
            form = SendMessageForm(request.POST)
            sub = "Reply"

            if form.is_valid():                     # All validation rules pass
                content = form.cleaned_data['content']


        if form.is_valid():

            # creates new message
            messages.add_message(request, messages.INFO, 'Reply Sent.', extra_tags='alert-success')
            AlertMessage.create(currentUser, UserProfile.objects.get(id=msg.sender.id), sub, content, False, 0).save()
        
            if AlertMessage.objects.get(id=message_id).subject != "Request":
                return HttpResponseRedirect('/messagecenter/message/' + message_id)
      
            return HttpResponseRedirect('/messagecenter/delete/' + str(msg.id))     # Redirect after POST

        return render(request, 'messageCenter/viewMessage.html', {'msg': msg, 'form': form, 'formError': True,
                                                                  'doesConflict': doesConflict})

    else:   # Message is being read, not replied to

        if msg.subject == "Request":    # Checks if message is a request
            form = SendMessageForm()

            for r in existingReservations:

                # Checks for reservation conflicts
                if not ((msg.startDate < r.startDate and msg.endDate < r.startDate) or
                            (msg.startDate >= r.endDate and msg.endDate > r.endDate)):
                        doesConflict = True

        else:
            form = SendMessageForm()                    # An unbound form
    
    
    return render(request, 'messageCenter/viewMessage.html', {'msg': msg, 'form': form, 'formError': False,
                                                              'doesConflict': doesConflict})
    


def inboxView(request):
    """Lists user's messages
    """

    if not request.user.is_authenticated:
        return HttpResponseRedirect('/login/')
    
    if (request.user.is_staff):
        allMessages= AlertMessage.objects.all()
    else:
        currentUser = UserProfile.objects.get(user_id=request.user.id)
        
        
        allMessages = AlertMessage.objects.filter( receiver__user_id=currentUser.user_id ).order_by('id').reverse()
                                            
    return render(request, 'messageCenter/inboxView.html', {
        'allMessages': allMessages, 'numMessages': len(allMessages)
    })



def sendMessage(request, user_id):
    """Called to create a new message
    """
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/login/')
    else:
        currentUser = UserProfile.objects.get(user_id=request.user.id)
    if request.method == 'POST':                 # If the form has been submitted...
        form = SendMessageForm(request.POST)         # A form bound to the POST data
        if form.is_valid():                     # All validation rules pass
            content = form.cleaned_data['content']
            
            #creates new tool
            try:
                AlertMessage.create(currentUser, UserProfile.objects.get(user_id=user_id), "Message", content, False, 0).save()
            except:
                return HttpResponseRedirect('ERROR')
            messages.add_message(request, messages.INFO, 'Message Sent.', extra_tags='alert-success')
            return HttpResponseRedirect('/tooldirectory/')     # Redirect after POST
    else:
        form = SendMessageForm()                     # An unbound form
    
    
                                            
    return render(request, 'messageCenter/sendMessage.html', {
        'form': form, 'user_id': user_id, 'receiver':User.objects.get(id=user_id)
    })
    

def sendToolRequest(request, toolId):
    """ Called to send a request for a tool
    """

    if not request.user.is_authenticated:
        return HttpResponseRedirect('/login/')
    else:
        currentUser = UserProfile.objects.get(user_id=request.user.id)
        currTool = ToolModel.objects.get(id=toolId)
    curRes = Reservation.objects.filter(tool_id=toolId, endDate__gt=date.today())
    conflictingReservations = []
        
    if request.method == 'POST':                 # If the form has been submitted...
        form = MakeRequest(request.POST)         # A form bound to the POST data
        if form.is_valid():                     # All validation rules pass
            startDate = form.cleaned_data['startDate']
            endDate = form.cleaned_data['endDate']
            message = form.cleaned_data['message']
            
            if message != "":
                message = "Personal message for tool request: " + message
            else:
                message = ""
            
            if (endDate < startDate):
                form = MakeRequest()
                return render(request, 'messageCenter/sendRequest.html', {
                    'form': form, 'toolId': toolId, 'conflict': True, 'conflicts': conflictingReservations, 'curRes': curRes, 'tool': ToolModel.objects.get(id=toolId)
                })
            

            existingReservations = Reservation.objects.filter(tool_id=toolId)
            
            for r in existingReservations:
                if not ((startDate < r.startDate and endDate < r.startDate) or (startDate >= r.endDate and endDate > r.endDate)):
                        conflictingReservations.append(r)          
                    
            if len(conflictingReservations) > 0:
                form = MakeRequest()
                return render(request, 'messageCenter/sendRequest.html', {
                    'form': form, 'toolId': toolId, 'conflict': True, 'conflicts': conflictingReservations, 'curRes':curRes, 'tool': ToolModel.objects.get(id=toolId)
                })
              
            
            if currTool.inShed():
                Reservation.create(currTool, currentUser, startDate, endDate).save()
                content = User.objects.get(id=currentUser.user_id).username + " is borrowing "\
                 + ToolModel.objects.get(id=toolId).name + "  from your shed from " + startDate.strftime("%m/%d/%y") \
                 + " to " + endDate.strftime("%m/%d/%y") + ".\n" + message
                
                shed = CommunityShed.objects.get(id=currTool.location_id)
                messages.add_message(request, messages.INFO, 'Your reservation has been created.', extra_tags='alert-success')
                AlertMessage.create(currentUser, UserProfile.objects.get(id=shed.owner_id), "Message", content, False, toolId, startDate, endDate).save()
                
                currentUser.timesBorrowed += 1
                currentUser.save()
        
                currTool.timesUsed += 1
                currTool.save()
                
                return HttpResponseRedirect('/tooldirectory/')
                
            if not currTool.inShed():
                content = (User.objects.get(id=currentUser.user_id).username) + " has requested to borrow your "\
                    + ToolModel.objects.get(id=toolId).name + " from " + startDate.strftime("%m/%d/%y") + " to " + endDate.strftime("%m/%d/%y") + ".\n" + message

                messages.add_message(request, messages.INFO, 'Your request has been sent.', extra_tags='alert-success')
                AlertMessage.create(currentUser, UserProfile.objects.get(id=currTool.owner_id), "Request", content, True, toolId, startDate, endDate).save()

                
                return HttpResponseRedirect('/tooldirectory/')     # Redirect after POST
    else:
        form = MakeRequest()                     # An unbound form
        
    return render(request, 'messageCenter/sendRequest.html', {
        'form': form, 'toolId': toolId, 'conflict': False, 'curRes':curRes, 'tool': ToolModel.objects.get(id=toolId)
    })
    
    
def approveRequest(request, message_id, toolId):
    """ Called when tool request is approved
    """

    message=AlertMessage.objects.get(id=message_id)
    sender=message.sender
    currTool=ToolModel.objects.get(id=message.toolId)
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/login/')
    else:
        existingReservations = Reservation.objects.filter(tool_id=message.toolId)
        currentUser = UserProfile.objects.get(user_id=request.user.id)
        for r in existingReservations:
                if not ((message.startDate < r.startDate and message.endDate < r.startDate) or (message.startDate >= r.endDate and message.endDate > r.endDate)):
                        return HttpResponseRedirect('/messagecenter/')
        
    content = (User.objects.get(id=currentUser.user_id).username) + " has approved of your request to borrow " + ToolModel.objects.get(id=toolId).name\
         + " from " + message.startDate.strftime("%m/%d/%y") + " to " + message.endDate.strftime("%m/%d/%y") + '.'

    try:
        t = ToolModel.objects.get(id=toolId)
        #t.available = False
        #t.save()
        
        Reservation.create(currTool, sender, message.startDate, message.endDate).save()
        
        AlertMessage.create(currentUser, UserProfile.objects.get(user_id=sender.user_id), "Request Approved", content, False, 0).save()
        
        sender.timesBorrowed += 1
        sender.save()
        
        currentUser.timesLent += 1
        currentUser.save()
        
        t.timesUsed += 1
        t.save()
    except:
        return HttpResponseRedirect('ERROR')
    
    return HttpResponseRedirect('/messagecenter/delete/'+message_id)

def myReservations(request):
    """ View user's past, present, and future reservations
    """

    if not request.user.is_authenticated:
        return HttpResponseRedirect('/login/')
    else:
        currentUser = UserProfile.objects.get(user_id=request.user.id)
        if request.user.is_staff:
            reservations= Reservation.objects.all()
        else:
            reservations = Reservation.objects.filter(borrower_id=currentUser.id)
        past = reservations.filter(endDate__lte=date.today()).order_by('-endDate','-startDate')
        present = reservations.filter(endDate__gt=date.today(), startDate__lte=date.today())
        future = reservations.filter(startDate__gt=date.today())
    return render (request, 'messagecenter/reservationslist.html', {
                    'reservations': reservations, 'past': past, 'present': present, 'future': future})
    
def deleteReservation(request, reservation_id):
    """Called to delete a reservation
    """

    try:
        reservation = Reservation.objects.get(id=reservation_id)
    except:
        return HttpResponseRedirect('/messagecenter/reservations')

    if request.user.is_authenticated:
        reservation.delete()
        
    return HttpResponseRedirect('/messagecenter/reservations')

def returnReservation(request, reservation_id):
    """Called to return a tool early
    """

    try:
        reservation = Reservation.objects.get(id=reservation_id)
    except:
        return HttpResponseRedirect('/messagecenter/reservations')
    if request.user.is_authenticated:
        reservation.endDate=date.today()
        reservation.save()
    return HttpResponseRedirect('/messagecenter/reservations')



def deleteMessage(request, message_id):
    """ Called to delete a message form user's inbox
    """

    try:
        msg = AlertMessage.objects.get(id=message_id)
    except:
        return HttpResponseRedirect('/messagecenter/')
    if request.user.is_authenticated:
        currentUser = UserProfile.objects.get(user_id=request.user.id)
        print(msg.receiver)
        print(request.user.username)
        if (User.objects.get(id=msg.receiver.user_id).username==request.user.username or request.user.is_staff):
            msg.delete()
            if msg.subject=='Request':
                #messages.add_message(request, messages.INFO, 'Reply Sent.', extra_tags='alert-info')
                pass
            else:
                messages.add_message(request, messages.INFO, 'Message Deleted.', extra_tags='alert-danger')
            
    return HttpResponseRedirect('/messagecenter/')
