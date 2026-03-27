from messageCenter.models import AlertMessage
from tests.api.base import APITestBase
from tests.test_config import TEST_MESSAGE_MAX_LENGTH


class MessagesAPIComponentTests(APITestBase):
    def setUp(self):
        self.sender_user, self.sender_profile = self.create_user_with_profile(
            "senderuser",
            first_name="Sender",
            last_name="User",
        )
        self.receiver_user, self.receiver_profile = self.create_user_with_profile(
            "receiveruser",
            first_name="Receiver",
            last_name="User",
        )
        self.base_message = self.create_message(self.sender_profile, self.receiver_profile)

    def test_NEGATIVE_CREATE_message_requires_authentication(self):
        response = self.client.get(f"/messagecenter/sendMessage/{self.receiver_user.id}/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "/login/")

    def test_POSITIVE_CREATE_message(self):
        self.client.force_login(self.sender_user)
        response = self.client.post(
            f"/messagecenter/sendMessage/{self.receiver_user.id}/",
            {"content": "Hello from component tests"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "/tooldirectory/")
        self.assertTrue(
            AlertMessage.objects.filter(
                sender=self.sender_profile,
                receiver=self.receiver_profile,
                content="Hello from component tests",
            ).exists()
        )

    def test_NEGATIVE_CREATE_message_rejects_content_over_1000_characters(self):
        self.client.force_login(self.sender_user)
        oversized_content = "x" * (TEST_MESSAGE_MAX_LENGTH + 1)
        before_count = AlertMessage.objects.count()
        response = self.client.post(
            f"/messagecenter/sendMessage/{self.receiver_user.id}/",
            {"content": oversized_content},
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(AlertMessage.objects.count(), before_count)

    def test_POSITIVE_CREATE_message_model_save_path_truncates_content_over_1000_characters(self):
        oversized_content = "y" * (TEST_MESSAGE_MAX_LENGTH + 1)
        msg = AlertMessage.create(
            self.sender_profile,
            self.receiver_profile,
            "Message",
            oversized_content,
            False,
            0,
        )
        msg.save()
        msg.refresh_from_db()
        self.assertEqual(len(msg.content), TEST_MESSAGE_MAX_LENGTH)

    def test_POSITIVE_READ_inbox_view(self):
        self.client.force_login(self.receiver_user)
        response = self.client.get("/messagecenter/")
        self.assertEqual(response.status_code, 200)

    def test_POSITIVE_READ_message_view_marks_message_as_read(self):
        self.client.force_login(self.receiver_user)
        self.assertFalse(self.base_message.read)
        response = self.client.get(f"/messagecenter/message/{self.base_message.id}/")
        self.assertEqual(response.status_code, 200)
        self.base_message.refresh_from_db()
        self.assertTrue(self.base_message.read)

    def test_POSITIVE_UPDATE_message_view_creates_reply_message(self):
        self.client.force_login(self.receiver_user)
        response = self.client.post(
            f"/messagecenter/message/{self.base_message.id}/",
            {"content": "Reply content from receiver"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(AlertMessage.objects.filter(subject="Reply", content="Reply content from receiver").exists())

    def test_POSITIVE_DELETE_message(self):
        self.client.force_login(self.receiver_user)
        response = self.client.get(f"/messagecenter/delete/{self.base_message.id}/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "/messagecenter/")
        self.assertFalse(AlertMessage.objects.filter(id=self.base_message.id).exists())

    def test_NEGATIVE_DELETE_message_as_non_receiver_is_ignored(self):
        self.client.force_login(self.sender_user)
        response = self.client.get(f"/messagecenter/delete/{self.base_message.id}/")
        self.assertEqual(response.status_code, 302)
        self.assertTrue(AlertMessage.objects.filter(id=self.base_message.id).exists())

    # TODO: Add component tests for approveRequest workflow edge-cases (conflicts and missing tool).
