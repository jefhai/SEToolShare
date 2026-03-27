from shareCenter.models import CommunityShed
from tests.api.base import APITestBase


class ShedsAPIComponentTests(APITestBase):
    def setUp(self):
        self.user, self.profile = self.create_user_with_profile("sheduser", first_name="Shed", last_name="Owner")

    def test_NEGATIVE_CREATE_shed_requires_authentication(self):
        response = self.client.get("/sharecenter/createshed/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "/login/")

    def test_POSITIVE_CREATE_shed(self):
        self.client.force_login(self.user)
        response = self.client.post("/sharecenter/createshed/", {"address": "9 Birch Rd", "city": "Rochester"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "/tooldirectory/")
        self.assertTrue(CommunityShed.objects.filter(owner=self.profile, address="9 Birch Rd").exists())

    def test_POSITIVE_READ_shed(self):
        self.client.force_login(self.user)
        self.create_shed(self.profile, address="12 Willow Ave")
        response = self.client.get(f"/sharecenter/shed/{self.user.username}/")
        self.assertEqual(response.status_code, 200)

    def test_POSITIVE_READ_shed_list(self):
        self.client.force_login(self.user)
        self.create_shed(self.profile, address="21 Cedar St")
        response = self.client.get("/sharecenter/shedlist/")
        self.assertEqual(response.status_code, 200)

    def test_POSITIVE_DELETE_shed(self):
        self.client.force_login(self.user)
        self.create_shed(self.profile, address="88 Meadow Ct")
        response = self.client.get("/sharecenter/deleteshed/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "/tooldirectory/")
        self.assertFalse(CommunityShed.objects.filter(owner=self.profile).exists())

    # TODO: No shed update endpoint exists today; component update coverage is not applicable yet.
    # TODO: Input validation currently does not prevent creating duplicate sheds per user.
