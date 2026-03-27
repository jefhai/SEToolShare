from datetime import date, timedelta

from messageCenter.models import Reservation
from tests.api.base import APITestBase


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

    # TODO: Input validation currently does not enforce reservation ownership on update/delete endpoints.
    # TODO: Add component tests for request-approval lifecycle in approveRequest endpoint.
