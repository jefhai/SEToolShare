from datetime import date, timedelta

from messageCenter.models import AlertMessage
from messageCenter.models import Reservation
from tests.api.base import APITestBase
from tests.test_config import TEST_MESSAGE_MAX_LENGTH


class ReservationsAPIComponentTests(APITestBase):
    def setUp(self):
        self.owner_user, self.owner_profile = self.create_user_with_profile(
            "resowner",
            first_name="Res",
            last_name="Owner",
        )
        self.borrower_user, self.borrower_profile = self.create_user_with_profile(
            "resborrower",
            first_name="Res",
            last_name="Borrower",
            zip_code=self.owner_profile.zipCode,
        )
        self.owner_shed = self.create_shed(self.owner_profile)
        self.tool = self.create_tool(self.owner_profile, name="Shared Saw", location=self.owner_shed)

    def test_NEGATIVE_CREATE_reservation_requires_authentication(self):
        response = self.client.get(f"/messagecenter/sendrequest/{self.tool.id}/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "/login/")

    def test_POSITIVE_CREATE_reservation_via_send_request(self):
        self.client.force_login(self.borrower_user)
        start_date = date.today() + timedelta(days=2)
        end_date = start_date + timedelta(days=3)
        response = self.client.post(
            f"/messagecenter/sendrequest/{self.tool.id}/",
            {
                "startDate": start_date.isoformat(),
                "endDate": end_date.isoformat(),
                "message": "Looking forward to this project.",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "/tooldirectory/")
        self.assertTrue(
            Reservation.objects.filter(
                tool=self.tool,
                borrower=self.borrower_profile,
                startDate=start_date,
                endDate=end_date,
            ).exists()
        )

    def test_POSITIVE_READ_my_reservations(self):
        self.client.force_login(self.borrower_user)
        reservation = Reservation.create(
            self.tool,
            self.borrower_profile,
            date.today() - timedelta(days=1),
            date.today() + timedelta(days=1),
        )
        reservation.save()
        response = self.client.get("/messagecenter/reservations/")
        self.assertEqual(response.status_code, 200)

    def test_POSITIVE_UPDATE_return_reservation_sets_end_today(self):
        reservation = Reservation.create(
            self.tool,
            self.borrower_profile,
            date.today() - timedelta(days=2),
            date.today() + timedelta(days=4),
        )
        reservation.save()
        self.client.force_login(self.borrower_user)
        response = self.client.get(f"/messagecenter/reservations/return/{reservation.id}/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "/messagecenter/reservations")
        reservation.refresh_from_db()
        self.assertEqual(reservation.endDate, date.today())

    def test_POSITIVE_DELETE_reservation(self):
        reservation = Reservation.create(
            self.tool,
            self.borrower_profile,
            date.today() + timedelta(days=2),
            date.today() + timedelta(days=5),
        )
        reservation.save()
        self.client.force_login(self.borrower_user)
        response = self.client.get(f"/messagecenter/reservations/delete/{reservation.id}/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "/messagecenter/reservations")
        self.assertFalse(Reservation.objects.filter(id=reservation.id).exists())

    def test_NEGATIVE_DELETE_reservation_missing_record_redirects_list(self):
        self.client.force_login(self.borrower_user)
        response = self.client.get("/messagecenter/reservations/delete/999999/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "/messagecenter/reservations")

    def test_POSITIVE_CREATE_send_request_allows_1000_char_message_after_envelope_merge(self):
        self.client.force_login(self.borrower_user)
        start_date = date.today() + timedelta(days=1)
        end_date = start_date + timedelta(days=1)
        boundary_message = "x" * TEST_MESSAGE_MAX_LENGTH
        response = self.client.post(
            f"/messagecenter/sendrequest/{self.tool.id}/",
            {
                "startDate": start_date.isoformat(),
                "endDate": end_date.isoformat(),
                "message": boundary_message,
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "/tooldirectory/")
        self.assertTrue(
            AlertMessage.objects.filter(
                sender=self.borrower_profile,
                receiver=self.owner_profile,
                toolId=self.tool.id,
            ).exists()
        )
        self.assertTrue(
            Reservation.objects.filter(
                tool=self.tool,
                borrower=self.borrower_profile,
                startDate=start_date,
                endDate=end_date,
            ).exists()
        )

    def test_NEGATIVE_CREATE_send_request_rejects_raw_message_over_1000(self):
        self.client.force_login(self.borrower_user)
        start_date = date.today() + timedelta(days=1)
        end_date = start_date + timedelta(days=1)
        response = self.client.post(
            f"/messagecenter/sendrequest/{self.tool.id}/",
            {
                "startDate": start_date.isoformat(),
                "endDate": end_date.isoformat(),
                "message": "z" * (TEST_MESSAGE_MAX_LENGTH + 1),
            },
        )
        self.assertEqual(response.status_code, 400)

    def test_POSITIVE_UPDATE_approve_request_creates_reservation_and_approval_message(self):
        start_date = date.today() + timedelta(days=3)
        end_date = start_date + timedelta(days=2)
        request_message = AlertMessage.create(
            self.borrower_profile,
            self.owner_profile,
            "Request",
            "Could I borrow this tool for a project?",
            True,
            self.tool.id,
            start_date,
            end_date,
        )
        request_message.save()

        before_borrowed = self.borrower_profile.timesBorrowed
        before_lent = self.owner_profile.timesLent
        before_tool_used = self.tool.timesUsed

        self.client.force_login(self.owner_user)
        response = self.client.get(f"/messagecenter/approverequest/{request_message.id}/{self.tool.id}/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], f"/messagecenter/delete/{request_message.id}")

        self.assertTrue(
            Reservation.objects.filter(
                tool=self.tool,
                borrower=self.borrower_profile,
                startDate=start_date,
                endDate=end_date,
            ).exists()
        )
        self.assertTrue(
            AlertMessage.objects.filter(
                sender=self.owner_profile,
                receiver=self.borrower_profile,
                subject="Request Approved",
            ).exists()
        )

        self.borrower_profile.refresh_from_db()
        self.owner_profile.refresh_from_db()
        self.tool.refresh_from_db()
        self.assertEqual(self.borrower_profile.timesBorrowed, before_borrowed + 1)
        self.assertEqual(self.owner_profile.timesLent, before_lent + 1)
        self.assertEqual(self.tool.timesUsed, before_tool_used + 1)

    def test_NEGATIVE_UPDATE_approve_request_with_conflict_redirects_without_side_effects(self):
        start_date = date.today() + timedelta(days=5)
        end_date = start_date + timedelta(days=2)
        existing = Reservation.create(
            self.tool,
            self.borrower_profile,
            start_date,
            end_date,
        )
        existing.save()

        other_user, other_profile = self.create_user_with_profile(
            "requester2",
            first_name="Second",
            last_name="Requester",
            zip_code=self.owner_profile.zipCode,
        )
        request_message = AlertMessage.create(
            other_profile,
            self.owner_profile,
            "Request",
            "Conflicting request",
            True,
            self.tool.id,
            start_date,
            end_date,
        )
        request_message.save()

        before_res_count = Reservation.objects.count()
        self.client.force_login(self.owner_user)
        response = self.client.get(f"/messagecenter/approverequest/{request_message.id}/{self.tool.id}/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "/messagecenter/")
        self.assertEqual(Reservation.objects.count(), before_res_count)
        self.assertFalse(
            AlertMessage.objects.filter(
                sender=self.owner_profile,
                receiver=other_profile,
                subject="Request Approved",
            ).exists()
        )
        _ = other_user

    def test_NEGATIVE_UPDATE_approve_request_with_missing_tool_redirects_error(self):
        start_date = date.today() + timedelta(days=6)
        end_date = start_date + timedelta(days=1)
        request_message = AlertMessage.create(
            self.borrower_profile,
            self.owner_profile,
            "Request",
            "Request with bad tool route",
            True,
            self.tool.id,
            start_date,
            end_date,
        )
        request_message.save()

        self.client.force_login(self.owner_user)
        response = self.client.get(f"/messagecenter/approverequest/{request_message.id}/999999/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "ERROR")

    def test_NEGATIVE_UPDATE_approve_request_requires_authentication(self):
        start_date = date.today() + timedelta(days=4)
        end_date = start_date + timedelta(days=2)
        request_message = AlertMessage.create(
            self.borrower_profile,
            self.owner_profile,
            "Request",
            "Please approve this request",
            True,
            self.tool.id,
            start_date,
            end_date,
        )
        request_message.save()

        response = self.client.get(f"/messagecenter/approverequest/{request_message.id}/{self.tool.id}/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "/login/")

    # TODO: Input validation currently does not enforce reservation ownership on update/delete endpoints.
