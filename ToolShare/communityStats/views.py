from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.template import RequestContext, loader
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.conf import settings
from django.contrib.auth.models import User
from login.models import DemoUserScope
from shareCenter.models import ToolModel, UserProfile
from messageCenter.models import Reservation
from datetime import date


def _scoped_demo_profiles(current_user):
    demo_scope = DemoUserScope.objects.filter(user=current_user).first()
    if demo_scope is None:
        return None
    contact_username = getattr(settings, 'DEMO_CONTACT_USERNAME', 'jefhai')
    return UserProfile.objects.filter(
        user__demouserscope__scope=demo_scope.scope
    ) | UserProfile.objects.filter(user__username=contact_username)

def statReport(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect("/login/")

    currentUser = UserProfile.objects.get(user_id=request.user.id)

    #Staff defaults
    if (request.user.is_staff):
        zipCode = 'ADMIN'
        allUsers = UserProfile.objects.all()
        allTools = ToolModel.objects.all()
        numUsers = len(allUsers) - 1
    else:
        demo_profiles = _scoped_demo_profiles(request.user)
        if demo_profiles is not None:
            allUsers = demo_profiles
            allTools = ToolModel.objects.filter(owner__in=demo_profiles)
        else:
            allUsers = UserProfile.objects.filter(zipCode=currentUser.zipCode)
            allTools = ToolModel.objects.filter(owner__zipCode=currentUser.zipCode)
        numUsers = len(allUsers)


    # We need 6 pieces of information:


    # Most Borrowed Tools
    mostBorrowed = allTools.order_by('-timesUsed')
    if len(mostBorrowed) > 5:
        mostBorrowed = mostBorrowed[0:5]

    # Least Borrowed Tools
    leastBorrowed = allTools.order_by('timesUsed')
    if len(leastBorrowed) > 5:
        leastBorrowed = leastBorrowed[0:5]

    # Recently Borrowed Tools

    recentlyBorrowed = []
    toolQuerys = []

    for t in allTools:
        toolQuerys.append(Reservation.objects.filter(tool__id=t.id, startDate__lte=date.today()).order_by('-startDate'))

    for t in toolQuerys:
        if len(t) > 0:
            recentlyBorrowed.append(t[0])

    recentlyBorrowed.sort(key=lambda x: x.startDate, reverse=True)


    if len(recentlyBorrowed) > 5:
        recentlyBorrowed = recentlyBorrowed[0:5]



    # Top Lenders
    topLenders = allUsers.order_by('-timesLent')
    if len(topLenders) > 5:
        topLenders = topLenders[0:5]


    # Top Borrowers
    topBorrowers = allUsers.order_by('-timesBorrowed')
    if len(topBorrowers) > 5:
        topBorrowers = topBorrowers[0:5]

    # Most Active Overall Users
    mostActivity = UserProfile.objects.extra(
        select={'activityCount': 'timesLent + timesBorrowed'}, order_by=('-activityCount',)
    )
    demo_profiles = _scoped_demo_profiles(request.user)
    if demo_profiles is not None:
        mostActivity = mostActivity.filter(id__in=demo_profiles.values_list('id', flat=True))
    else:
        mostActivity = mostActivity.filter(zipCode=currentUser.zipCode)

    if len(mostActivity) > 5:
        mostActivity = mostActivity[0:5]




    """
    #Determines who's the highest lender
    highLender = allUsers[0]
    for u in allUsers:
        if (u.timesLent > highLender.timesLent):
            highLender = u

    #Determines who's the highest borrower
    highBorrower = allUsers[0]
    for u in allUsers:
        if (u.timesBorrowed > highBorrower.timesBorrowed):
            highBorrower = u

    #Determines the most used tool
    allTools = ToolModel.objects.filter(owner__zipCode=currentUser.zipCode)
    mostUsedTool = allTools[0]
    for t in allTools:
        if (t.timesUsed > mostUsedTool.timesUsed):
            mostUsedTool = t

    #Determines the most recently used tool
    endDates = Reservation.objects.filter(borrower__zipCode=currentUser.zipCode)
    previousEndDate = endDates[0]
    for ed in endDates:
        if (ed.endDate >= date.today() and ed.endDate <= previousEndDate.endDate):
            mostRecentlyUsedTool = ToolModel.objects.get(id=ed.tool_id)
        previousEndDate = ed
        """



    #Render stats page
    return render(request, 'communitystats/stats.html',  { 'mostBorrowed': mostBorrowed, 'leastBorrowed': leastBorrowed,
                                                           'recentlyBorrowed': recentlyBorrowed,
                                                           'topLenders': topLenders, 'topBorrowers': topBorrowers, 'mostActivity':mostActivity})
