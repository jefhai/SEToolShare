from django.contrib.auth.models import User
from django.test.utils import override_settings

from shareCenter.models import UserProfile
from tests.api.base import APITestBase


class RegistrationAPIComponentTests(APITestBase):
    def _valid_registration_payload(self, **overrides):
        payload = {
            "firstName": "Jamie",
            "lastName": "Gardner",
            "streetAddress": "12 Pine St",
            "city": "Rochester",
            "state": "NY",
            "zipcode": "14623",
            "email": "jamie.gardner@example.com",
            "username": "jamiegardner",
            "password": "pass12345",
            "confirmPassword": "pass12345",
        }
        payload.update(overrides)
        return payload

    def test_POSITIVE_CREATE_registration_creates_user_and_profile(self):
        response = self.client.post("/registration/", self._valid_registration_payload())
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "/login/")
        created_user = User.objects.get(username="jamiegardner")
        self.assertTrue(UserProfile.objects.filter(user=created_user).exists())

    def test_NEGATIVE_CREATE_registration_rejects_password_mismatch(self):
        payload = self._valid_registration_payload(confirmPassword="different")
        response = self.client.post("/registration/", payload)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="jamiegardner").exists())

    def test_NEGATIVE_CREATE_registration_duplicate_username_redirects_error(self):
        self.create_user_with_profile("jamiegardner", email="existing@example.com")
        response = self.client.post("/registration/", self._valid_registration_payload())
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "#ERROR")

    def test_NEGATIVE_CREATE_registration_rejects_non_numeric_zipcode(self):
        payload = self._valid_registration_payload(zipcode="14A2B")
        response = self.client.post("/registration/", payload)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="jamiegardner").exists())

    def test_NEGATIVE_CREATE_registration_rejects_zipcode_not_five_digits(self):
        payload = self._valid_registration_payload(zipcode="1462")
        response = self.client.post("/registration/", payload)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="jamiegardner").exists())

    def test_POSITIVE_CREATE_registration_preserves_leading_zero_zipcode(self):
        payload = self._valid_registration_payload(username="zipleadingzero", email="zip.leading@example.com", zipcode="01234")
        response = self.client.post("/registration/", payload)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "/login/")
        created_user = User.objects.get(username="zipleadingzero")
        created_profile = UserProfile.objects.get(user=created_user)
        self.assertEqual(created_profile.zipCode, "01234")

    @override_settings(DISABLE_USER_REGISTRATION=True)
    def test_POSITIVE_READ_registration_page_shows_disabled_message_when_registration_off(self):
        response = self.client.get("/registration/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Registration is currently disabled")
        self.assertContains(response, "disabled")

    @override_settings(DISABLE_USER_REGISTRATION=True)
    def test_NEGATIVE_CREATE_registration_returns_400_when_registration_disabled(self):
        response = self.client.post("/registration/", self._valid_registration_payload())
        self.assertEqual(response.status_code, 400)
        self.assertContains(response, "Registration is currently disabled", status_code=400)
        self.assertFalse(User.objects.filter(username="jamiegardner").exists())

    # TODO: Add component tests for email-normalization and username character constraints.
