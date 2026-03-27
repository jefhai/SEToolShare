from django.contrib.auth.models import User
from django.test import TestCase
from django.test.utils import override_settings

from messageCenter.models import AlertMessage
from shareCenter.models import CommunityShed, ToolModel, UserProfile
from tests.test_config import TEST_GLOBAL_CONFIG


@override_settings(**TEST_GLOBAL_CONFIG)
class APITestBase(TestCase):
    def create_user_with_profile(
        self,
        username,
        *,
        password="pass12345",
        first_name="Test",
        last_name="User",
        email=None,
        zip_code="14623",
        street_address="100 Maple St",
        city="Rochester",
        state="NY",
        is_staff=False,
        is_superuser=False,
    ):
        if email is None:
            email = f"{username}@example.com"
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )
        user.is_staff = is_staff
        user.is_superuser = is_superuser
        user.save()

        profile = UserProfile.create(user, zip_code, street_address, state, city)
        profile.save()
        return user, profile

    def create_shed(self, owner_profile, *, address="200 Grove Ave", city=None, zipcode=None):
        if city is None:
            city = owner_profile.city
        if zipcode is None:
            zipcode = owner_profile.zipCode
        shed = CommunityShed.create(owner_profile, address, city, zipcode)
        shed.save()
        return shed

    def create_tool(
        self,
        owner_profile,
        *,
        name="Cordless Drill",
        description="Reliable tool for weekend projects.",
        pickup_information="Porch pickup after 5pm.",
        location=None,
        available=True,
    ):
        tool = ToolModel.create(
            owner_profile,
            name,
            description,
            pickup_information,
            location,
            available,
        )
        tool.save()
        return tool

    def create_message(self, sender_profile, receiver_profile, *, subject="Message", content="Hello there"):
        msg = AlertMessage.create(sender_profile, receiver_profile, subject, content, False, 0)
        msg.save()
        return msg
