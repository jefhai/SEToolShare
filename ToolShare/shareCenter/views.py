from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.template import RequestContext, loader
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.conf import settings
from django.contrib.auth.models import User
from shareCenter.models import ToolModel, UserProfile, AddToolForm, EditToolForm, EditPassword, EditUserInfoForm, AddCommunityShedForm, CommunityShed, ToolSearchForm
from messageCenter.models import Reservation, AlertMessage
from django.contrib import messages
from datetime import date
from django.utils import formats

# Add tool method
def addTool(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/login/')


    possibleLocations = [(0, 'Home')]

    if not request.user.is_staff:
        currentUser = UserProfile.objects.get(user_id=request.user.id)
        sheds = CommunityShed.objects.filter(zipcode=currentUser.zipCode)

        for shed in sheds:
            shedOwner = User.objects.get(id=shed.owner.user_id)
            possibleLocations.append((shed.id, shedOwner.username + '\'s Shed'))

    if request.method == 'POST':                                # If the form has been submitted...
        form = AddToolForm(possibleLocations, request.POST)     # A form bound to the POST data
        if form.is_valid():                                     # All validation rules pass

            # Form data
            name = form.cleaned_data['name']
            description = form.cleaned_data['description']
            location = form.cleaned_data['location']
            pickupInformation = form.cleaned_data['pickup_info']
            available = form.cleaned_data['available']

            # Checks to see if location is home(None) or not
            loc = None
            if location > 0:
                loc = CommunityShed.objects.get(id=location)

            # Try to create new tool
            try:
                ToolModel.create(currentUser, name, description,
                                 pickupInformation, loc, available).save()
            except:
                return HttpResponseRedirect('ERROR')

            # Redirect if tool creation succeeds
            messages.add_message(request, messages.INFO, 'New tool has been added.', extra_tags='alert-success')
            return HttpResponseRedirect('/tooldirectory/')
    else:
        form = AddToolForm(possibleLocations)    # An unbound form

    return render(request, 'shareCenter/addtool.html', {'form': form})

#************************************************************************************

def deleteTool(request, tool_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/login/')

    tool = get_object_or_404(ToolModel, id=tool_id)
    if tool.owner.user_id != request.user.id and not request.user.is_staff:
        messages.add_message(request, messages.INFO, 'Only the tool owner can delete this tool.', extra_tags='alert-danger')
        return HttpResponse('Authorization error: cannot delete tool you do not own.', status=400)

    tool.delete()

    return HttpResponseRedirect('/sharecenter/user/' + request.user.username)

#************************************************************************************

# Add tool directory method    
def toolDirectory(request):
    filtered = False
    page_size = getattr(settings, 'TOOLS_DIRECTORY_PAGE_SIZE', 20)
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/login/')
    possibleLocations = [(-1, 'All'), (0, 'Home')]

    if not (request.user.is_staff):
        currentUser = UserProfile.objects.get(user_id=request.user.id)
        sheds = CommunityShed.objects.filter(zipcode=currentUser.zipCode)
    else:
        sheds = CommunityShed.objects.all()

    for shed in sheds:
        shedOwner = User.objects.get(id=shed.owner.user_id)
        possibleLocations.append((shed.id, shedOwner.username + '\'s Shed'))

    currentUser = UserProfile.objects.get(user_id=request.user.id)

    if (request.user.is_staff):
        zipCode = 'ADMIN'
        alltools = ToolModel.objects.all()
    else:
        communityMembers = UserProfile.objects.filter(zipCode=currentUser.zipCode)
        zipCode = currentUser.zipCode
        alltools = ToolModel.objects.filter(owner_id__zipCode=currentUser.zipCode).order_by('-id')

    request_params = request.GET
    if request_params:
        form = ToolSearchForm(possibleLocations, request_params)
        if form.is_valid():

            searchTerms = form.cleaned_data['searchTerms']
            filter = form.cleaned_data['filter']
            location = form.cleaned_data['location']

            #Filter by Location
            if location == -1:
                pass
            elif location == 0:
                filtered = True
                alltools = alltools.filter(location=None)
            else:
                filtered = True
                alltools = alltools.filter(location_id=location)

            if filter == 'DA':
                alltools = alltools.order_by('-id')
            elif filter == 'NA':
                filtered = True
                alltools = alltools.order_by('name')
            elif filter == 'OW':
                filtered = True
                alltools = alltools.order_by('owner__user__username')

            if searchTerms != '':
                filtered = True
                alltools = alltools.filter(name__icontains=searchTerms)

    else:
        form = ToolSearchForm(possibleLocations)

    paginator = Paginator(alltools, page_size)
    page_obj = paginator.get_page(request.GET.get('page'))

    query_params = request.GET.copy()
    if 'page' in query_params:
        query_params.pop('page')
    pagination_query = query_params.urlencode()

    return render(request, 'shareCenter/tooldirectory.html', {
        'alltools': page_obj.object_list,
        'page_obj': page_obj,
        'zipCode': zipCode,
        'numTools': paginator.count,
        'hasShed': currentUser.hasShed(),
        'form': form,
        'filtered': filtered,
        'pagination_query': pagination_query,
    })

#************************************************************************************ 

# Add tool info method 
def toolInfo(request, tool_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/login/')

    tool = get_object_or_404(ToolModel, pk=tool_id)

    tName = tool.name
    tDesc = tool.description
    pickupInfo = tool.pickupInformation
    availability = tool.available
    toolId = tool.id

    toolLocation = tool.location        #Turning ze location into a string so we can put it on the page
    tLoc = ''
    if toolLocation == None:
        tLoc = 'Owner\'s Home'
    else:
        tLoc += toolLocation.owner.user.username
        tLoc += "'s shed"                #location has been stringified

    owner = UserProfile.objects.get(id=tool.owner_id)
    ownerEmail = (User.objects.get(id=owner.user_id)).email
    ownerUsername = (User.objects.get(id=owner.user_id)).username

    # Data for Google Maps Directions/Info Page
    userAddress = UserProfile.objects.get(user_id=request.user.id).sAddress + ", " + UserProfile.objects.get(
        user_id=request.user.id).city + ", " + UserProfile.objects.get(user_id=request.user.id).state
    ownerAddress = ""
    wellFormatedAddress = ""
    if not request.user.is_staff:
        if tool.inShed():
            ownerAddress = toolLocation.address + ", " + toolLocation.city + ", " + owner.state
            wellFormatedAddress = toolLocation.address + "\n" + toolLocation.city + ", " + owner.state + " " + owner.zipCode
        else:
            ownerAddress = owner.sAddress + ", " + owner.city + ", " + owner.state
            wellFormatedAddress = owner.sAddress + "\n" + owner.city + ", " + owner.state + " " + owner.zipCode

    return render(request, 'sharecenter/toolinfo.html', {
        'tName': tName, 'tDesc': tDesc, 'ownerEmail': ownerEmail,
        'pickupInfo': pickupInfo, 'availability': availability,
        'ownerUsername': ownerUsername, 'ownerId': owner.user_id, 'tool': tool, 'tLoc': tLoc,
        'ownerAddress': ownerAddress, 'userAddress': userAddress, 'wellFormatedAddress': wellFormatedAddress})

#************************************************************************************

#User Profile Page    
def userProfile(request, username):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/login/')

    user = get_object_or_404(User, username=username)
    currUser = request.user

    uProfile = UserProfile.objects.get(user_id=user.id)
    fName = user.first_name
    lName = user.last_name
    zipCode = uProfile.zipCode
    sAddress = uProfile.sAddress
    city = uProfile.city
    state = uProfile.state
    email = user.email

    #list of user's tools
    userTools = ToolModel.objects.filter(owner_id__id=uProfile.id)
    userId = user.id
    timesLent = uProfile.timesLent
    timesBorrowed = uProfile.timesBorrowed

    return render(request, 'sharecenter/userprofile.html', {
        'username': username, 'fName': fName, 'lName': lName,
        'zipCode': zipCode, 'sAddress': sAddress, 'city': city, 'state': state,
        'userTools': userTools, 'numTools': len(userTools), 'currUser': currUser,
        'timesLent': timesLent, 'timesBorrowed': timesBorrowed, 'userId': userId, 'email': email})

#************************************************************************************  

def createShed(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/login/')

    uProfile = UserProfile.objects.get(user_id=request.user.id)

    if request.method == 'POST':
        form = AddCommunityShedForm(request.POST)
        if form.is_valid():

            address = form.cleaned_data['address']
            city = form.cleaned_data['city']

            duplicate_shed_exists = CommunityShed.objects.filter(
                owner=uProfile,
                address__iexact=address.strip(),
                city__iexact=city.strip(),
                zipcode=uProfile.zipCode,
            ).exists()
            if duplicate_shed_exists:
                messages.add_message(request, messages.INFO, 'Duplicate shed is not allowed for this user.', extra_tags='alert-danger')
                return render(request, 'sharecenter/createshed.html', {'form': AddCommunityShedForm()}, status=400)

            try:
                CommunityShed.create(uProfile, address, city, uProfile.zipCode).save()
            except:
                return HttpResponseRedirect('Error')
            return HttpResponseRedirect('/tooldirectory/')
    else:
        form = AddCommunityShedForm()
    return render(request, 'sharecenter/createshed.html', {'form': form})

#************************************************************************************

def manageShed(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/login/')

    # Checks if use has a shed
    uProfile = UserProfile.objects.get(user_id=request.user.id)
    if not (uProfile.hasShed()):
        return HttpResponseRedirect('/tooldirectory')

    shed = CommunityShed.objects.get(owner=uProfile.id)
    shedId = shed.id
    shedTools = ToolModel.objects.filter(location_id=shed.id)
    owner = UserProfile.objects.get(id=shed.owner_id)
    ownerUsername = (User.objects.get(id=owner.user_id)).username

    return render(request, 'sharecenter/manageshed.html', {
        'shedId': shedId, 'shedTools': shedTools, 'username': ownerUsername})

#************************************************************************************   

def shed(request, username):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/login/')

    user = get_object_or_404(User, username=username)

    # Checks if user has a shed
    uProfile = UserProfile.objects.get(user_id=user.id)
    if not (uProfile.hasShed()):
        return HttpResponseRedirect('/tooldirectory')

    shed = CommunityShed.objects.get(owner_id=uProfile.id)
    shedId = shed.id
    shedTools = ToolModel.objects.filter(location_id=shed.id)
    owner = UserProfile.objects.get(id=shed.owner_id)
    ownerUsername = (User.objects.get(id=owner.user_id)).username

    return render(request, 'sharecenter/shed.html', {
        'shed_id': shedId, 'shedTools': shedTools, 'numTools': len(shedTools), 'username': ownerUsername})

#************************************************************************************    

def shedList(request):
    page_size = getattr(settings, 'SHEDS_DIRECTORY_PAGE_SIZE', 20)
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/login/')

    if (request.user.is_staff):
        zipCode = 'ADMIN'
        sheds = CommunityShed.objects.all().order_by('-id')
        hasShed = False
    else:
        currentUser = UserProfile.objects.get(user_id=request.user.id)
        sheds = CommunityShed.objects.filter(zipcode=currentUser.zipCode).order_by('-id')
        zipCode = currentUser.zipCode
        hasShed = currentUser.hasShed()

    paginator = Paginator(sheds, page_size)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'sharecenter/shedlist.html', {
        'sheds': page_obj.object_list,
        'page_obj': page_obj,
        'zipCode': zipCode,
        'numSheds': paginator.count,
        'hasShed': hasShed,
    })

#************************************************************************************    

def editTool(request, tool_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/login/')


    currTool = get_object_or_404(ToolModel, pk=tool_id)
    possibleLocations = [(0, 'Home')]

    if not (request.user.is_staff):
        currentUser = UserProfile.objects.get(user_id=request.user.id)
        sheds = CommunityShed.objects.filter(zipcode=currentUser.zipCode)

        for shed in sheds:
            shedOwner = User.objects.get(id=shed.owner.user_id)
            possibleLocations.append((shed.id, shedOwner.username + '\'s Shed'))
            print(shed.id)

    if request.method == 'POST':                                # If the form has been submitted...
        form = EditToolForm(possibleLocations, request.POST)    # A form bound to the POST data
        if form.is_valid():                                     # All validation rules pass

            # Form data
            name = form.cleaned_data['name']
            description = form.cleaned_data['description']
            location = form.cleaned_data['location']
            pickupInformation = form.cleaned_data['pickup_info']
            available = form.cleaned_data['available']

            # Checks to see if location is home(None) or not
            loc = None
            if location > 0:
                loc = CommunityShed.objects.get(id=location)

            # Tries to edit existing tool
            try:
                currTool.name = name
                currTool.description = description
                currTool.pickupInformation = pickupInformation
                currTool.location = loc
                currTool.available = available
                messages.add_message(request, messages.INFO, 'Tool info updated.', extra_tags='alert-success')
                currTool.save()

            except:
                return HttpResponseRedirect('ERROR')    # Redirect to error
            return HttpResponseRedirect('/tooldirectory/')     # Redirect after POST

    else:
        initLoc = 0
        if currTool.location_id != None:
            initLoc = currTool.location.id
        form = EditToolForm(possibleLocations, initial={'name': currTool.name, 'description': currTool.description,
                                                        'pickup_info': currTool.pickupInformation, 'location': initLoc,
                                                        'available': currTool.available})    # An unbound form

    return render(request, 'shareCenter/edittool.html', {
        'form': form, 'tool_id': tool_id})

#************************************************************************************

def editUserInfo(request, username):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/login/')


    user = get_object_or_404(User, username=username)
    currentUser = UserProfile.objects.get(user_id=user.id)

    if request.method == 'POST':                         # If the form has been submitted...
        form = EditUserInfoForm(request.POST)         # A form bound to the POST data
        if form.is_valid():                         # All validation rules pass

            # Form data
            fName = form.cleaned_data['firstName']
            lName = form.cleaned_data['lastName']
            email = form.cleaned_data['email']
            sAddress = form.cleaned_data['streetAddress']
            city = form.cleaned_data['city']
            state = form.cleaned_data['state']
            zcode = form.cleaned_data['zipcode'].strip().zfill(5)
            if zcode != currentUser.zipCode:
                changeZipCode(request);

                # Tries to create a new user and add them to the database
            try:
                user.first_name = fName
                user.last_name = lName
                user.email = email
                currentUser.sAddress = sAddress
                currentUser.city = city
                currentUser.state = state
                currentUser.zipCode = zcode
                currentUser.save()
                user.save()
            except:
                #Add error
                return HttpResponseRedirect('#ERROR')
            messages.add_message(request, messages.INFO, 'Your Information has been Updated.', extra_tags='alert-success')
            return HttpResponseRedirect('/tooldirectory/')     # Redirect after POST
    else:
        form = EditUserInfoForm(initial={'firstName': user.first_name, 'lastName': user.last_name, 'email': user.email,
                                         'streetAddress': currentUser.sAddress, 'city': currentUser.city,
                                         'state': currentUser.state,
                                         'zipcode': str(currentUser.zipCode).zfill(5)})                     # An unbound form

    return render(request, 'shareCenter/edituserinfo.html', {'form': form, 'username': username})

#************************************************************************************ 

def changeZipCode(request):
    currentUser = UserProfile.objects.get(user_id=request.user.id)
    Reservation.objects.filter(tool__owner__id=currentUser.id).delete()
    AlertMessage.objects.filter(receiver=currentUser.id, isRequest=True).delete()
    ToolModel.objects.filter(owner_id=currentUser.id).update(location=None)
    if currentUser.hasShed():
        userShed = CommunityShed.objects.get(owner_id=currentUser.id)
        ToolModel.objects.filter(location=userShed).update(location=None)
        userShed.delete()

#************************************************************************************

def editPassword(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/login/')


    user = get_object_or_404(User, username=request.user.username)
    currentUser = UserProfile.objects.get(user_id=user.id)

    if request.method == 'POST':                # If the form has been submitted...
        form = EditPassword(request.user, request.POST)         # A form bound to the POST data
        if form.is_valid():                         # All validation rules pass
            pwd = form.cleaned_data['password']

            # Tries to edit password and saves to the database
            try:
                user.set_password(pwd)
                user.save()
            except:
                #Add error
                messages.add_message(request, messages.INFO, 'An Error Has Occured.', extra_tags='alert-danger')
                return HttpResponseRedirect('#ERROR')
            messages.add_message(request, messages.INFO, 'Password successfully changed.', extra_tags='alert-success')
            return HttpResponseRedirect('/sharecenter/user/' + request.user.username)     # Redirect after POST
    else:
        form = EditPassword(request.user)                     # An unbound form

    return render(request, 'shareCenter/editpassword.html', {'form': form})

    #************************************************************************************

def userDirectory(request):
    page_size = getattr(settings, 'USERS_DIRECTORY_PAGE_SIZE', 20)
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/login/')
    currentUser = UserProfile.objects.get(user_id=request.user.id)

    if (request.user.is_staff):
        zipCode = 'ADMIN'
        allUsers = UserProfile.objects.all().order_by('user__username')
        numUsers = max(allUsers.count() - 1, 0) #Adjust for admin

    else:
        zipCode = currentUser.zipCode
        allUsers = UserProfile.objects.filter(zipCode=currentUser.zipCode).order_by('user__username')
        numUsers = allUsers.count()

    paginator = Paginator(allUsers, page_size)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'sharecenter/userdirectory.html', {
        'zipCode': zipCode,
        'allUsers': page_obj.object_list,
        'page_obj': page_obj,
        'numUsers': numUsers,
    })

#************************************************************************************

def changeToolState(request, tool_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/login/')

    if len(ToolModel.objects.filter(id=tool_id)) == 0:
        return HttpResponseRedirect('/sharecenter/shed/' + request.user.username)

    currTool = ToolModel.objects.get(id=tool_id)
    currUser = get_object_or_404(UserProfile, user_id=request.user.id)
    if (currTool.location_id != get_object_or_404(CommunityShed, owner_id=currUser.id).id) or (request.user.is_staff):
        return HttpResponseRedirect('/home/')

    if currTool.available:
        currTool.available = False
    else:
        currTool.available = True
    currTool.save()

    return HttpResponseRedirect('/sharecenter/shed/' + request.user.username)

#************************************************************************************

def deleteShed(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/login/')
    currentUser = UserProfile.objects.get(user_id=request.user.id)
    myShed = CommunityShed.objects.filter(owner_id=currentUser.id)
    if len(myShed) == 0:
        return HttpResponseRedirect('/tooldirectory/')
    myShed = CommunityShed.objects.get(owner_id=currentUser.id)
    allTools = ToolModel.objects.filter(owner__zipCode=currentUser.zipCode, location=myShed.id)

    for t in allTools:
        t.location = None
        print(t.name)
        t.save()
        content = "Your " + t.name + " has been returned to you and marked as Home Sharing because " + myShed.owner.user.username + "'s shed has been removed."
        AlertMessage.create(currentUser, t.owner, "Alert", content, False).save()

    myShed.delete()
    return HttpResponseRedirect('/tooldirectory/')














