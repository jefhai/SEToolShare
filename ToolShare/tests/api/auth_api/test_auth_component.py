from tests.api.base import APITestBase


class AuthAPIComponentTests(APITestBase):
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

    # TODO: Add component tests for security controls such as lockout and throttling.
