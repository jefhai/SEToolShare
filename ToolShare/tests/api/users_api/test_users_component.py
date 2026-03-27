from django.contrib.auth.models import User

from shareCenter.models import UserProfile
from tests.api.base import APITestBase


class UsersAPIComponentTests(APITestBase):
    def setUp(self):
        self.user, self.profile = self.create_user_with_profile(
            "profileuser",
            password="oldpassword123",
            first_name="Profile",
            last_name="User",
            email="profileuser@example.com",
        )
        self.create_tool(self.profile, name="Profile Hammer")

    def test_POSITIVE_READ_user_profile(self):
        self.client.force_login(self.user)
        response = self.client.get(f"/sharecenter/user/{self.user.username}/")
        self.assertEqual(response.status_code, 200)

    def test_POSITIVE_READ_user_directory(self):
        self.client.force_login(self.user)
        response = self.client.get("/sharecenter/userdirectory/")
        self.assertEqual(response.status_code, 200)

    def test_POSITIVE_UPDATE_edit_user_info(self):
        self.client.force_login(self.user)
        payload = {
            "firstName": "Updated",
            "lastName": "Neighbor",
            "streetAddress": "19 Cedar Ave",
            "city": "Rochester",
            "state": "NY",
            "zipcode": "14620",
            "email": "updated@example.com",
        }
        response = self.client.post(f"/sharecenter/edituser/{self.user.username}/", payload)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "/tooldirectory/")
        self.user.refresh_from_db()
        self.profile.refresh_from_db()
        self.assertEqual(self.user.first_name, "Updated")
        self.assertEqual(self.profile.zipCode, "14620")

    def test_POSITIVE_UPDATE_edit_password(self):
        self.client.force_login(self.user)
        response = self.client.post(
            "/sharecenter/editpassword/",
            {
                "oldPassword": "oldpassword123",
                "password": "newpassword123",
                "confirmPassword": "newpassword123",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], f"/sharecenter/user/{self.user.username}")
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("newpassword123"))

    def test_NEGATIVE_UPDATE_edit_password_rejects_invalid_old_password(self):
        self.client.force_login(self.user)
        response = self.client.post(
            "/sharecenter/editpassword/",
            {
                "oldPassword": "wrong-old-password",
                "password": "newpassword123",
                "confirmPassword": "newpassword123",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("oldpassword123"))

    def test_POSITIVE_READ_edit_user_info_shows_leading_zero_zipcode(self):
        self.profile.zipCode = "01234"
        self.profile.save(update_fields=["zipCode"])
        self.client.force_login(self.user)
        response = self.client.get(f"/sharecenter/edituser/{self.user.username}/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'value="01234"')

    # TODO: No user-delete endpoint exists today; delete component coverage is not applicable yet.
    # TODO: Input validation currently allows editing other users via URL without ownership checks.
