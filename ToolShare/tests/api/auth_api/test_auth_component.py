from tests.api.base import APITestBase
from datetime import date, timedelta
from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone
from login.models import DemoUserScope
from messageCenter.models import AlertMessage, Reservation
from shareCenter.models import CommunityShed, ToolModel, UserProfile


class AuthAPIComponentTests(APITestBase):
    def _extract_demo_scope(self, email):
        scope_row = DemoUserScope.objects.filter(user__email=email).first()
        if scope_row is None:
            return None
        return scope_row.scope

    def setUp(self):
        self.user, self.profile = self.create_user_with_profile(
            "authuser",
            password="pass12345",
            first_name="Auth",
            last_name="User",
        )

    def test_POSITIVE_CREATE_login_session_with_valid_credentials(self):
        response = self.client.post("/login/", {"username": "authuser", "password": "pass12345"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "/tooldirectory/")
        self.assertIn("_auth_user_id", self.client.session)

    def test_NEGATIVE_CREATE_login_session_with_invalid_credentials(self):
        response = self.client.post("/login/", {"username": "authuser", "password": "wrongpass"})
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_POSITIVE_READ_home_page(self):
        response = self.client.get("/home/")
        self.assertEqual(response.status_code, 200)

    def test_POSITIVE_READ_credits_page(self):
        response = self.client.get("/login/credits/")
        self.assertEqual(response.status_code, 200)

    def test_POSITIVE_DELETE_logout_session(self):
        self.client.force_login(self.user)
        response = self.client.get("/logout/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "/login/")

    def test_POSITIVE_CREATE_demo_user_from_demo_route(self):
        before_user_count = User.objects.count()

        response = self.client.get("/demo/")

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "/tooldirectory/")
        self.assertIn("_auth_user_id", self.client.session)

        self.assertGreaterEqual(User.objects.count(), before_user_count + 11)
        demo_user = User.objects.get(id=self.client.session["_auth_user_id"])
        self.assertTrue(demo_user.username.startswith("alexmorgan"))
        self.assertTrue(demo_user.email.startswith(demo_user.username))
        self.assertTrue(demo_user.email.endswith("@example.com"))
        self.assertEqual(demo_user.first_name, "Alex")
        self.assertEqual(demo_user.last_name, "Morgan")

    def test_POSITIVE_CREATE_isolated_demo_profile_and_seed_data(self):
        response = self.client.get("/demo/")
        self.assertEqual(response.status_code, 302)

        demo_user = User.objects.get(id=self.client.session["_auth_user_id"])
        demo_profile = UserProfile.objects.get(user=demo_user)

        self.assertEqual(demo_profile.sAddress, "1 Lomb Memorial Dr")
        self.assertEqual(demo_profile.city, "Rochester")
        self.assertEqual(demo_profile.state, "NY")
        self.assertEqual(demo_profile.zipCode, "14623")

        self.assertGreaterEqual(UserProfile.objects.filter(zipCode="14623").count(), 11)
        self.assertGreaterEqual(CommunityShed.objects.filter(owner__zipCode="14623").count(), 11)
        self.assertGreaterEqual(ToolModel.objects.filter(owner__zipCode="14623").count(), 22)

        demo_user_tools = ToolModel.objects.filter(owner=demo_profile)
        self.assertGreaterEqual(demo_user_tools.count(), 3)
        self.assertGreaterEqual(demo_user_tools.filter(location__owner=demo_profile).count(), 2)

        reserved_tools_count = Reservation.objects.values_list("tool_id", flat=True).distinct().count()
        self.assertGreaterEqual(reserved_tools_count, demo_user_tools.count())

        active_reservations = Reservation.objects.filter(startDate__lte=date.today(), endDate__gt=date.today()).count()
        self.assertGreaterEqual(active_reservations, 1)

        incoming_requests = AlertMessage.objects.filter(receiver=demo_profile, isRequest=True).count()
        self.assertGreaterEqual(incoming_requests, 2)

        contact_username = getattr(settings, "DEMO_CONTACT_USERNAME", "jefhai")
        self.assertTrue(User.objects.filter(username=contact_username).exists())
        welcome_message = AlertMessage.objects.filter(receiver=demo_profile, sender__user__username=contact_username).first()
        self.assertIsNotNone(welcome_message)
        self.assertIn("jefhai.com", welcome_message.content)
        self.assertIn("linkedin.com", welcome_message.content)
        self.assertIn("github.com", welcome_message.content)

        demo_borrowed = Reservation.objects.filter(borrower=demo_profile)
        self.assertGreaterEqual(demo_borrowed.filter(endDate__lte=date.today()).count(), 1)
        self.assertGreaterEqual(demo_borrowed.filter(startDate__lte=date.today(), endDate__gt=date.today()).count(), 1)
        self.assertGreaterEqual(demo_borrowed.filter(startDate__gt=date.today()).count(), 1)

        demo_tools_reserved = Reservation.objects.filter(tool__owner=demo_profile).exclude(borrower=demo_profile)
        self.assertGreaterEqual(demo_tools_reserved.filter(startDate__lte=date.today(), endDate__gt=date.today()).count(), 1)
        self.assertGreaterEqual(demo_tools_reserved.filter(startDate__gt=date.today()).count(), 1)
        self.assertGreater(demo_profile.timesBorrowed, 0)
        self.assertGreater(demo_profile.timesLent, 0)

        active_profiles = UserProfile.objects.filter(zipCode="14623", timesBorrowed__gt=0, timesLent__gt=0)
        self.assertGreaterEqual(active_profiles.count(), 5)

        scope = self._extract_demo_scope(demo_user.email)
        self.assertIsNotNone(scope)
        scoped_users = User.objects.filter(demouserscope__scope=scope, demouserscope__role="neighbor").count()
        self.assertGreaterEqual(scoped_users, 10)

        directory_response = self.client.get("/sharecenter/userdirectory/")
        self.assertEqual(directory_response.status_code, 200)
        self.assertContains(directory_response, contact_username)

    def test_POSITIVE_DELETE_expired_demo_users_when_new_demo_is_created(self):
        old_user, old_profile = self.create_user_with_profile("oldstudent12")
        old_user.email = "oldstudent12@example.com"
        old_user.date_joined = timezone.now() - timedelta(hours=2)
        old_user.save()
        DemoUserScope.objects.create(user=old_user, scope="oldscope", role="student")

        old_neighbor_user, old_neighbor_profile = self.create_user_with_profile("oldneighbor34")
        old_neighbor_user.email = "oldneighbor34@example.com"
        old_neighbor_user.save()
        DemoUserScope.objects.create(user=old_neighbor_user, scope="oldscope", role="neighbor")

        response = self.client.get("/demo/")

        self.assertEqual(response.status_code, 302)
        self.assertFalse(User.objects.filter(id=old_user.id).exists())
        self.assertFalse(UserProfile.objects.filter(id=old_profile.id).exists())
        self.assertFalse(User.objects.filter(id=old_neighbor_user.id).exists())
        self.assertFalse(UserProfile.objects.filter(id=old_neighbor_profile.id).exists())
        contact_username = getattr(settings, "DEMO_CONTACT_USERNAME", "jefhai")
        self.assertTrue(User.objects.filter(username=contact_username).exists())

    def test_POSITIVE_CREATE_new_demo_when_stale_demo_session_interacts(self):
        response = self.client.get("/demo/")
        self.assertEqual(response.status_code, 302)
        old_demo_user_id = self.client.session["_auth_user_id"]

        User.objects.filter(id=old_demo_user_id).delete()
        session = self.client.session
        session["is_demo_session"] = True
        session.save()

        redirected = self.client.get("/home/", follow=True)

        self.assertEqual(redirected.redirect_chain[0][0], "/demo/")
        self.assertTrue(User.objects.filter(id=self.client.session["_auth_user_id"]).exists())
        self.assertNotEqual(str(old_demo_user_id), str(self.client.session["_auth_user_id"]))

    def test_POSITIVE_CREATE_new_demo_session_when_previous_demo_expired(self):
        first_demo = self.client.get("/demo/")
        self.assertEqual(first_demo.status_code, 302)

        expired_demo_user_id = self.client.session["_auth_user_id"]
        expired_demo_user = User.objects.get(id=expired_demo_user_id)
        expired_scope = self._extract_demo_scope(expired_demo_user.email)
        self.assertIsNotNone(expired_scope)

        expired_demo_user.date_joined = timezone.now() - timedelta(hours=2)
        expired_demo_user.save()

        second_demo = self.client.get("/demo/")
        self.assertEqual(second_demo.status_code, 302)
        self.assertEqual(second_demo["Location"], "/tooldirectory/")

        new_demo_user_id = self.client.session["_auth_user_id"]
        self.assertNotEqual(str(expired_demo_user_id), str(new_demo_user_id))
        self.assertFalse(User.objects.filter(id=expired_demo_user_id).exists())
        self.assertEqual(DemoUserScope.objects.filter(scope=expired_scope).count(), 0)

    # TODO: Add component tests for security controls such as lockout and throttling.
