from shareCenter.models import ToolModel
from tests.api.base import APITestBase


class ToolsAPIComponentTests(APITestBase):
    def setUp(self):
        self.owner_user, self.owner_profile = self.create_user_with_profile(
            "toolowner",
            first_name="Tool",
            last_name="Owner",
        )
        self.other_user, self.other_profile = self.create_user_with_profile(
            "otheruser",
            first_name="Other",
            last_name="User",
        )
        self.owner_shed = self.create_shed(self.owner_profile)
        self.tool = self.create_tool(self.owner_profile, name="Hammer", location=self.owner_shed)

    def test_NEGATIVE_CREATE_add_tool_requires_authentication(self):
        response = self.client.get("/sharecenter/addtool/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "/login/")

    def test_POSITIVE_CREATE_add_tool_creates_record(self):
        self.client.force_login(self.owner_user)
        payload = {
            "name": "New Drill",
            "description": "Excellent condition drill.",
            "pickup_info": "Porch handoff.",
            "location": 0,
            "available": "on",
        }
        response = self.client.post("/sharecenter/addtool/", payload)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "/tooldirectory/")
        self.assertTrue(ToolModel.objects.filter(name="New Drill", owner=self.owner_profile).exists())

    def test_POSITIVE_READ_tool_directory(self):
        self.client.force_login(self.owner_user)
        response = self.client.get("/tooldirectory/")
        self.assertEqual(response.status_code, 200)

    def test_POSITIVE_READ_tool_detail(self):
        self.client.force_login(self.owner_user)
        response = self.client.get(f"/sharecenter/tool/{self.tool.id}/")
        self.assertEqual(response.status_code, 200)

    def test_POSITIVE_UPDATE_edit_tool(self):
        self.client.force_login(self.owner_user)
        payload = {
            "name": "Refined Hammer",
            "description": "Refined description.",
            "pickup_info": "Back porch.",
            "location": 0,
            "available": "on",
        }
        response = self.client.post(f"/sharecenter/tool/edit/{self.tool.id}/", payload)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "/tooldirectory/")
        self.tool.refresh_from_db()
        self.assertEqual(self.tool.name, "Refined Hammer")

    def test_POSITIVE_UPDATE_change_tool_state(self):
        self.client.force_login(self.owner_user)
        self.tool.available = True
        self.tool.location = self.owner_shed
        self.tool.save()
        response = self.client.get(f"/sharecenter/tool/changestate/{self.tool.id}/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], f"/sharecenter/shed/{self.owner_user.username}")
        self.tool.refresh_from_db()
        self.assertFalse(self.tool.available)

    def test_NEGATIVE_UPDATE_change_tool_state_non_owner_redirects_home(self):
        other_shed = self.create_shed(self.other_profile, address="404 Oak Ln")
        self.client.force_login(self.other_user)
        response = self.client.get(f"/sharecenter/tool/changestate/{self.tool.id}/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "/home/")
        _ = other_shed

    def test_POSITIVE_DELETE_tool(self):
        self.client.force_login(self.owner_user)
        response = self.client.get(f"/sharecenter/tool/delete/{self.tool.id}/")
        self.assertEqual(response.status_code, 302)
        self.assertFalse(ToolModel.objects.filter(id=self.tool.id).exists())

    # TODO: Input validation currently does not enforce ownership on deleteTool.
    # TODO: Add component tests for search filter combinations in Tool Directory.
