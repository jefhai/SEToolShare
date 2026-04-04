from django import forms
from django.db import transaction
import random
import uuid
from datetime import date, timedelta
from django.utils.crypto import get_random_string
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm
from django.template import RequestContext, loader
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth import login, logout
from login.models import DemoUserScope, loginForm
from shareCenter.models import CommunityShed, ToolModel, UserProfile
from messageCenter.models import AlertMessage, Reservation

DEMO_ZIPCODE = '14623'
DEMO_CITY = 'Rochester'
DEMO_STATE = 'NY'
DEMO_RIT_ADDRESS = '1 Lomb Memorial Dr'
DEMO_EMAIL_DOMAIN = 'example.com'

DEMO_PERSONAS = [
    ('Jordan', 'Reed', 'jordan.reed.demo01@example.com', '500 University Ave'),
    ('Avery', 'Cole', 'avery.cole.demo02@example.com', '353 Court St'),
    ('Cameron', 'Hayes', 'cameron.hayes.demo03@example.com', '657 East Ave'),
    ('Riley', 'Brooks', 'riley.brooks.demo04@example.com', '85 South Ave'),
    ('Parker', 'Shaw', 'parker.shaw.demo05@example.com', '1 Bausch and Lomb Pl'),
    ('Quinn', 'Foster', 'quinn.foster.demo06@example.com', '144 Exchange Blvd'),
    ('Taylor', 'Price', 'taylor.price.demo07@example.com', '1372 East Main St'),
    ('Morgan', 'Bell', 'morgan.bell.demo08@example.com', '1000 Elmwood Ave'),
    ('Casey', 'Ward', 'casey.ward.demo09@example.com', '90 Webster Crossing'),
    ('Hayden', 'Gray', 'hayden.gray.demo10@example.com', '1985 East Main St'),
    ('Rowan', 'James', 'rowan.james.demo11@example.com', '2825 Clover St'),
    ('Blake', 'Turner', 'blake.turner.demo12@example.com', '851 Joseph Ave'),
    ('Emerson', 'Perry', 'emerson.perry.demo13@example.com', '2222 St Paul St'),
    ('Drew', 'Bryant', 'drew.bryant.demo14@example.com', '171 Reservoir Ave'),
    ('Finley', 'Cruz', 'finley.cruz.demo15@example.com', '301 Exchange Blvd'),
    ('Sage', 'Long', 'sage.long.demo16@example.com', '500 Skyview Centre Pkwy'),
    ('Reese', 'Myers', 'reese.myers.demo17@example.com', '1115 East Main St'),
    ('Sydney', 'West', 'sydney.west.demo18@example.com', '1100 Goodman St N'),
    ('Logan', 'Fisher', 'logan.fisher.demo19@example.com', '500 Park Ave'),
    ('Peyton', 'Bennett', 'peyton.bennett.demo20@example.com', '3535 Winton Pl'),
    ('Harper', 'Sullivan', 'harper.sullivan.demo21@example.com', '50 Chestnut St'),
    ('Dakota', 'Barnes', 'dakota.barnes.demo22@example.com', '71 N Winton Rd'),
    ('Kendall', 'Russell', 'kendall.russell.demo23@example.com', '433 River St'),
    ('Skyler', 'Bishop', 'skyler.bishop.demo24@example.com', '1 Conservatory Dr'),
    ('Micah', 'Hunt', 'micah.hunt.demo25@example.com', '39 King St'),
    ('Jamie', 'Fox', 'jamie.fox.demo26@example.com', '316 Bay St'),
    ('Kai', 'Griffin', 'kai.griffin.demo27@example.com', '1100 University Ave'),
    ('Remy', 'Russell', 'remy.russell.demo28@example.com', '261 Dr Samuel McCree Way'),
    ('Shawn', 'Mills', 'shawn.mills.demo29@example.com', '370 East Ave'),
    ('Alexis', 'Diaz', 'alexis.diaz.demo30@example.com', '25 Gibbs St'),
    ('Elliot', 'Cook', 'elliot.cook.demo31@example.com', '1000 N River St'),
    ('Sawyer', 'Kelly', 'sawyer.kelly.demo32@example.com', '154 Pine Grove Ave'),
    ('Rory', 'Powell', 'rory.powell.demo33@example.com', '1501 Mt Hope Ave'),
    ('Noel', 'Bailey', 'noel.bailey.demo34@example.com', '1900 Empire Blvd'),
    ('Toby', 'Rivera', 'toby.rivera.demo35@example.com', '4600 Dewey Ave'),
    ('Milan', 'Sanders', 'milan.sanders.demo36@example.com', '2300 Ridgeway Ave'),
    ('Jules', 'Coleman', 'jules.coleman.demo37@example.com', '247 N Goodman St'),
    ('Ari', 'Henderson', 'ari.henderson.demo38@example.com', '1000 East River Rd'),
    ('Nico', 'Patel', 'nico.patel.demo39@example.com', '1044 University Ave'),
    ('Bailey', 'Nguyen', 'bailey.nguyen.demo40@example.com', '222 Hutchison Rd'),
    ('Robin', 'Flores', 'robin.flores.demo41@example.com', '1 Museum Dr'),
    ('Marley', 'Kim', 'marley.kim.demo42@example.com', '2800 Clover St'),
    ('Jesse', 'Baker', 'jesse.baker.demo43@example.com', '3700 Lake Ave'),
    ('Cory', 'Hill', 'cory.hill.demo44@example.com', '1200 Brooks Ave'),
    ('Frankie', 'Carter', 'frankie.carter.demo45@example.com', '2800 Elmwood Ave'),
    ('Devon', 'Watson', 'devon.watson.demo46@example.com', '1304 Pittsford-Mendon Rd'),
    ('Wren', 'Rogers', 'wren.rogers.demo47@example.com', '1 Vincent Tofany Blvd'),
    ('Kris', 'Murphy', 'kris.murphy.demo48@example.com', '800 East Ave'),
    ('Lane', 'Cooper', 'lane.cooper.demo49@example.com', '1775 Mt Hope Ave'),
    ('Sam', 'Howard', 'sam.howard.demo50@example.com', '880 Elmgrove Rd'),
]

DEMO_TOOL_CATALOG = [
    ('DEWALT 20V Max Drill Driver', 'Compact brushless drill with two batteries and charger.'),
    ('Makita Impact Driver Kit', '18V impact driver set for fasteners and deck screws.'),
    ('Milwaukee M18 Circular Saw', 'Cordless circular saw for wood and sheet cuts.'),
    ('Bosch Bulldog Rotary Hammer', 'SDS-plus rotary hammer for masonry anchors.'),
    ('Ryobi Orbital Sander', 'Random orbital sander with dust collection bag.'),
    ('Ridgid Shop Vac 16 Gallon', 'Wet/dry vacuum with hose and extension wand.'),
    ('Kobalt 230pc Socket Set', 'Full metric and SAE socket set in hard case.'),
    ('Stanley FatMax Tape + Level Kit', 'Layout kit with magnetic level and 35ft tape.'),
    ('Craftsman Mechanics Tool Set', 'Ratchets, sockets, and hex keys for bike/car work.'),
    ('EGO 56V Leaf Blower', 'Battery-powered blower with high-efficiency nozzle.'),
    ('Greenworks Hedge Trimmer', 'Cordless hedge trimmer with rotating handle.'),
    ('Worx JawSaw', 'Enclosed chainsaw for light branch cleanup tasks.'),
    ('Black+Decker Jig Saw', 'Variable-speed jigsaw with wood and metal blades.'),
    ('Dremel Rotary Tool 3000', 'Detail rotary kit for sanding, cutting, and polishing.'),
    ('Bissell Little Green', 'Portable carpet and upholstery spot cleaner.'),
    ('Anker Portable Work Light', 'Rechargeable LED flood light for evening repairs.'),
    ('Werner 6ft Step Ladder', 'Lightweight fiberglass ladder for indoor work.'),
    ('Kreg Pocket Hole Jig', 'Joinery jig with drill bit and depth stop.'),
    ('Fluke Non-Contact Tester', 'Electrical tester for safe outlet checks.'),
    ('Tile Cutter Pro 24in', 'Manual tile cutter for bathroom and kitchen projects.'),
    ('Campbell Hausfeld Air Compressor', 'Portable compressor with inflation accessories.'),
    ('50ft Outdoor Extension Cord', 'Heavy-duty grounded extension cord.'),
]

DEMO_PICKUP_NOTES = [
    'Porch pickup after class hours.',
    'Meet near the student union front doors.',
    'Available at the community shed on weekends.',
    'Pickup by appointment in the early evening.',
    'Weekday pickup available after 6pm.',
]

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


def _create_demo_username(first_name, last_name):
    base = ''.join(ch for ch in (first_name + last_name).lower() if ch.isalnum())
    while True:
        username = base + str(random.randint(10, 99))
        if not User.objects.filter(username=username).exists():
            return username


def _ensure_configured_contact_user():
    contact_username = getattr(settings, 'DEMO_CONTACT_USERNAME', '')
    if not contact_username:
        return None

    contact_email = getattr(settings, 'DEMO_CONTACT_EMAIL', 'contact@jefhai.com')
    contact_user, created = User.objects.get_or_create(
        username=contact_username,
        defaults={
            'email': contact_email,
            'first_name': 'Jef',
            'last_name': 'Hai',
        },
    )

    if created:
        contact_user.set_password(_random_uuid_password())
        contact_user.save(update_fields=['password'])

    contact_profile = UserProfile.objects.filter(user=contact_user).first()
    if contact_profile is None:
        contact_profile = UserProfile.create(
            contact_user,
            DEMO_ZIPCODE,
            DEMO_RIT_ADDRESS,
            DEMO_STATE,
            DEMO_CITY,
        )
        contact_profile.save()
    return contact_profile


def _send_demo_welcome_message(demo_profile):
    contact_profile = _ensure_configured_contact_user()
    if contact_profile is None:
        return

    base_message = getattr(
        settings,
        'DEMO_WELCOME_MESSAGE',
        'Thanks for trying the Tool Share demo experience.',
    )
    website = getattr(settings, 'DEMO_CONTACT_WEBSITE', 'jefhai.com')
    linkedin = getattr(settings, 'DEMO_CONTACT_LINKEDIN', 'https://www.linkedin.com/in/jefhai')
    github = getattr(settings, 'DEMO_CONTACT_GITHUB', 'https://github.com/jefhai')
    contact_email = getattr(settings, 'DEMO_CONTACT_EMAIL', 'contact@jefhai.com')
    website_url = website if website.startswith('http://') or website.startswith('https://') else 'https://' + website
    content = (
        'Hello,'
        + '\n\n'
        + base_message
        + '\n\nFind me or continue the conversation below.'
        + '\n\nWebsite: '
        + website_url
        + '\nLinkedIn: '
        + linkedin
        + '\nGitHub: '
        + github
        + '\nEmail: '
        + contact_email
        + '\n\nThank you,\nJeffrey Haines'
        + '\n\nDisclaimer: Replies to this message are not monitored.'
    )
    AlertMessage.create(
        contact_profile,
        demo_profile,
        'Welcome to Tool Share',
        content,
        False,
    ).save()


def _delete_demo_scope(scope):
    user_ids = DemoUserScope.objects.filter(scope=scope).values_list('user_id', flat=True)
    protected_username = getattr(settings, 'DEMO_CONTACT_USERNAME', 'jefhai')
    User.objects.filter(id__in=user_ids).exclude(username=protected_username).delete()


def _create_demo_tool(owner_profile, location):
    tool_name, description = random.choice(DEMO_TOOL_CATALOG)
    pickup_info = random.choice(DEMO_PICKUP_NOTES)
    ToolModel.create(
        owner_profile,
        tool_name,
        description,
        pickup_info,
        location,
        random.choice([True, True, True, False]),
    ).save()


def _random_uuid_password():
    return str(uuid.uuid4())


def _cleanup_expired_demo_users():
    cutoff = timezone.now() - timedelta(hours=1)
    expired_scopes = DemoUserScope.objects.filter(role='student', user__date_joined__lt=cutoff).values_list('scope', flat=True)
    for scope in set(expired_scopes):
        _delete_demo_scope(scope)


def _create_reservation(tool, borrower_profile, start_date, end_date):
    Reservation.create(tool, borrower_profile, start_date, end_date).save()


def _tool_is_available_for_range(tool, start_date, end_date):
    existing_reservations = Reservation.objects.filter(tool_id=tool.id)
    for reservation in existing_reservations:
        no_overlap = (end_date < reservation.startDate) or (start_date >= reservation.endDate)
        if not no_overlap:
            return False
    return True


def _pick_tool_for_range(tools, start_date, end_date):
    for tool in tools:
        if _tool_is_available_for_range(tool, start_date, end_date):
            return tool
    return None


def _seed_demo_reservations(all_tools, borrowers):
    today = date.today()
    reservable_tools = [tool for tool in all_tools if tool.available]
    if not reservable_tools or not borrowers:
        return

    target_count = max(1, int(len(reservable_tools) * 0.8))
    selected_tools = random.sample(reservable_tools, min(target_count, len(reservable_tools)))
    active_count = min(6, max(3, len(selected_tools) // 3), len(selected_tools))

    for index, tool in enumerate(selected_tools):
        borrower = random.choice(borrowers)
        if index < active_count:
            start_date = today - timedelta(days=random.randint(1, 4))
            end_date = today + timedelta(days=random.randint(2, 8))
        else:
            start_date = today + timedelta(days=random.randint(1, 24))
            end_date = start_date + timedelta(days=random.randint(2, 7))
        _create_reservation(tool, borrower, start_date, end_date)


def _seed_demo_requests_to_owner(demo_owner_profile, requesters, owner_tools):
    today = date.today()
    candidate_tools = [tool for tool in owner_tools if tool.available]
    if len(candidate_tools) < 2:
        for tool in owner_tools:
            if not tool.available:
                tool.available = True
                tool.save(update_fields=['available'])
                candidate_tools.append(tool)
            if len(candidate_tools) >= 2:
                break

    if len(candidate_tools) < 2 or len(requesters) < 2:
        return

    request_count = max(2, min(4, len(candidate_tools), len(requesters)))
    for requester, tool in zip(random.sample(requesters, request_count), random.sample(candidate_tools, request_count)):
        start_date = today + timedelta(days=random.randint(3, 21))
        end_date = start_date + timedelta(days=random.randint(2, 6))
        content = (
            requester.user.username
            + ' would like to borrow '
            + tool.name
            + ' from '
            + start_date.strftime('%m/%d/%y')
            + ' to '
            + end_date.strftime('%m/%d/%y')
            + '.'
        )
        AlertMessage.create(
            requester,
            demo_owner_profile,
            'Request',
            content,
            True,
            tool.id,
            start_date,
            end_date,
        ).save()


def _seed_demo_user_reservation_journey(demo_profile, neighbors):
    if not neighbors:
        return

    today = date.today()
    neighbor_tools = list(ToolModel.objects.filter(owner__in=neighbors, available=True).order_by('id'))
    demo_tools = list(ToolModel.objects.filter(owner=demo_profile, available=True).order_by('id'))

    if not neighbor_tools:
        return

    # Demo user borrowing history: extended past, current, and future.
    borrow_windows = [
        (today - timedelta(days=75), today - timedelta(days=70)),
        (today - timedelta(days=68), today - timedelta(days=63)),
        (today - timedelta(days=61), today - timedelta(days=56)),
        (today - timedelta(days=54), today - timedelta(days=49)),
        (today - timedelta(days=47), today - timedelta(days=42)),
        (today - timedelta(days=40), today - timedelta(days=34)),
        (today - timedelta(days=33), today - timedelta(days=29)),
        (today - timedelta(days=28), today - timedelta(days=23)),
        (today - timedelta(days=20), today - timedelta(days=14)),
        (today - timedelta(days=11), today - timedelta(days=6)),
        (today - timedelta(days=4), today + timedelta(days=2)),
        (today - timedelta(days=2), today + timedelta(days=4)),
        (today + timedelta(days=1), today + timedelta(days=5)),
        (today + timedelta(days=2), today + timedelta(days=7)),
        (today + timedelta(days=7), today + timedelta(days=12)),
        (today + timedelta(days=10), today + timedelta(days=15)),
        (today + timedelta(days=14), today + timedelta(days=20)),
        (today + timedelta(days=18), today + timedelta(days=24)),
        (today + timedelta(days=22), today + timedelta(days=28)),
        (today + timedelta(days=26), today + timedelta(days=32)),
    ]

    used_borrow_tool_ids = set()
    for start_date, end_date in borrow_windows:
        available_unique_tools = [tool for tool in neighbor_tools if tool.id not in used_borrow_tool_ids]
        tool = _pick_tool_for_range(available_unique_tools, start_date, end_date)
        if tool is not None:
            _create_reservation(tool, demo_profile, start_date, end_date)
            used_borrow_tool_ids.add(tool.id)

    # Demo owner's tools reserved by neighbors: more current and future.
    if demo_tools:
        lend_windows = [
            (today - timedelta(days=3), today + timedelta(days=1)),
            (today - timedelta(days=1), today + timedelta(days=5)),
            (today + timedelta(days=4), today + timedelta(days=10)),
            (today + timedelta(days=9), today + timedelta(days=14)),
            (today + timedelta(days=16), today + timedelta(days=22)),
        ]
        for start_date, end_date in lend_windows:
            tool = _pick_tool_for_range(demo_tools, start_date, end_date)
            if tool is not None:
                _create_reservation(tool, random.choice(neighbors), start_date, end_date)


def _update_demo_usage_counts(all_profiles, all_tools):
    def _realistic_count(base_count, low_mult, high_mult):
        if base_count <= 0:
            return 0
        value = (base_count * random.randint(low_mult, high_mult)) + random.randint(0, 9)
        if base_count >= 8 and random.random() < 0.35:
            value += random.randint(15, 45)
        return value

    for profile in all_profiles:
        borrowed_base = Reservation.objects.filter(borrower=profile).count()
        lent_base = Reservation.objects.filter(tool__owner=profile).count()
        profile.timesBorrowed = _realistic_count(borrowed_base, 7, 13)
        profile.timesLent = _realistic_count(lent_base, 7, 13)
        profile.save(update_fields=['timesBorrowed', 'timesLent'])

    for tool in all_tools:
        used_base = Reservation.objects.filter(tool=tool).count()
        tool.timesUsed = _realistic_count(used_base, 6, 12)
        tool.save(update_fields=['timesUsed'])


def _seed_demo_inbox_messages(demo_profile, neighbors):
    if len(neighbors) < 2:
        return

    message_templates = [
        'Thanks for sharing Tool Share with the neighborhood. The checkout flow is super clear.',
        'I tried the shed pickup process and it felt smooth. Nice UX updates.',
        'The reservation timeline is easy to follow now. Great improvement.',
        'I found a few tools I can use this weekend. Appreciate this platform!',
        'Tool details and pickup instructions are very clear. Helpful for first-time users.',
        'Thanks again for keeping the demo active. It is easy to understand and navigate.',
    ]

    random.shuffle(message_templates)
    senders = random.sample(neighbors, min(2, len(neighbors)))
    for sender, body in zip(senders, message_templates):
        AlertMessage.create(
            sender,
            demo_profile,
            'Message',
            body,
            False,
        ).save()


def startDemo(request):
    if request.user.is_authenticated:
        logout(request)

    _cleanup_expired_demo_users()

    with transaction.atomic():
        demo_scope = get_random_string(10, allowed_chars='abcdefghijklmnopqrstuvwxyz0123456789')
        username = _create_demo_username('Alex', 'Morgan')
        password = _random_uuid_password()
        demo_user = User.objects.create_user(
            username=username,
            email=username + '@' + DEMO_EMAIL_DOMAIN,
            password=password,
            first_name='Alex',
            last_name='Morgan',
        )
        DemoUserScope.objects.create(user=demo_user, scope=demo_scope, role='student')

        demo_profile = UserProfile.create(
            demo_user,
            DEMO_ZIPCODE,
            DEMO_RIT_ADDRESS,
            DEMO_STATE,
            DEMO_CITY,
        )
        demo_profile.save()

        demo_shed = CommunityShed.create(demo_profile, DEMO_RIT_ADDRESS, DEMO_CITY, DEMO_ZIPCODE)
        demo_shed.save()

        _create_demo_tool(demo_profile, demo_shed)
        _create_demo_tool(demo_profile, demo_shed)
        for _ in range(random.randint(1, 3)):
            _create_demo_tool(demo_profile, random.choice([None, demo_shed]))

        randomized_profiles = []
        random_user_count = random.randint(10, 15)
        random_shed_count = random.randint(10, 15)

        for first_name, last_name, email, address in random.sample(DEMO_PERSONAS, random_user_count):
            neighbor_username = _create_demo_username(first_name, last_name)
            neighbor_user = User.objects.create_user(
                username=neighbor_username,
                email=neighbor_username + '@' + DEMO_EMAIL_DOMAIN,
                password=_random_uuid_password(),
                first_name=first_name,
                last_name=last_name,
            )
            DemoUserScope.objects.create(user=neighbor_user, scope=demo_scope, role='neighbor')
            neighbor_profile = UserProfile.create(
                neighbor_user,
                DEMO_ZIPCODE,
                address,
                DEMO_STATE,
                DEMO_CITY,
            )
            neighbor_profile.save()
            randomized_profiles.append(neighbor_profile)

        shed_owners = random.sample(randomized_profiles, min(random_shed_count, len(randomized_profiles)))
        for shed_owner in shed_owners:
            shed = CommunityShed.create(shed_owner, shed_owner.sAddress, DEMO_CITY, DEMO_ZIPCODE)
            shed.save()
            for _ in range(random.randint(2, 4)):
                _create_demo_tool(shed_owner, random.choice([None, shed]))

        all_demo_profiles = [demo_profile] + randomized_profiles
        all_demo_tools = list(ToolModel.objects.filter(owner__in=all_demo_profiles))
        _seed_demo_reservations(all_demo_tools, randomized_profiles)
        _seed_demo_user_reservation_journey(demo_profile, randomized_profiles)
        demo_owner_tools = [tool for tool in all_demo_tools if tool.owner_id == demo_profile.id]
        _seed_demo_requests_to_owner(demo_profile, randomized_profiles, demo_owner_tools)
        _seed_demo_inbox_messages(demo_profile, randomized_profiles)
        _update_demo_usage_counts(all_demo_profiles, all_demo_tools)
        _send_demo_welcome_message(demo_profile)

    login(request, demo_user)
    request.session['is_demo_session'] = True
    return HttpResponseRedirect('/tooldirectory/')

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
    
