from shareCenter.models import CommunityShed
from tests.api.base import APITestBase
from tests.test_config import TEST_SHEDS_DIRECTORY_PAGE_SIZE


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

    def test_NEGATIVE_CREATE_shed_rejects_duplicate_for_same_user(self):
        self.client.force_login(self.user)
        payload = {"address": "9 Birch Rd", "city": "Rochester"}
        first = self.client.post("/sharecenter/createshed/", payload)
        second = self.client.post("/sharecenter/createshed/", payload)
        self.assertEqual(first.status_code, 302)
        self.assertEqual(second.status_code, 400)
        self.assertEqual(CommunityShed.objects.filter(owner=self.profile, address="9 Birch Rd", city="Rochester").count(), 1)

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

    def test_POSITIVE_READ_shed_list_supports_pagination(self):
        self.client.force_login(self.user)
        for i in range(TEST_SHEDS_DIRECTORY_PAGE_SIZE + 5):
            neighbor_profile = self.create_user_with_profile(
                f"shedowner{i:02d}",
                first_name=f"Owner{i:02d}",
                last_name="Shed",
                zip_code=self.profile.zipCode,
            )[1]
            self.create_shed(neighbor_profile, address=f"{300 + i} Paginated Ave")

        first_page = self.client.get("/sharecenter/shedlist/")
        second_page = self.client.get("/sharecenter/shedlist/?page=2")
        self.assertEqual(first_page.status_code, 200)
        self.assertEqual(second_page.status_code, 200)
        self.assertContains(first_page, "Page 1 of 2")
        self.assertContains(second_page, "Page 2 of 2")

    def test_POSITIVE_DELETE_shed(self):
        self.client.force_login(self.user)
        self.create_shed(self.profile, address="88 Meadow Ct")
        response = self.client.get("/sharecenter/deleteshed/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "/tooldirectory/")
        self.assertFalse(CommunityShed.objects.filter(owner=self.profile).exists())

    # TODO: No shed update endpoint exists today; component update coverage is not applicable yet.
