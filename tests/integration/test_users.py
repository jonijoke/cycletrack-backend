from sqlalchemy import select

import models
from tests.integration.base import IntegrationTestCase

URL = "/api/users/"


class UsersIntegrationTests(IntegrationTestCase):
    def get_saved_users(self) -> list[models.User]:
        return list(self.session.scalars(select(models.User)))

    def test_create_saves_user_to_database(self):
        response = self.client.post(
            URL, json={"username": "matti", "email": "matti@test.com"}
        )

        self.assertEqual(response.status_code, 201)
        body = response.json()
        saved = self.get_saved_users()
        self.assertEqual(len(saved), 1)
        self.assertEqual(saved[0].id, body["id"])
        self.assertEqual(saved[0].username, "matti")
        self.assertEqual(saved[0].email, "matti@test.com")

    def test_create_duplicate_returns_409_and_saves_only_once(self):
        payload = {"username": "matti", "email": "matti@test.com"}
        self.client.post(URL, json=payload)

        response = self.client.post(URL, json=payload)

        self.assertEqual(response.status_code, 409)
        self.assertEqual(len(self.get_saved_users()), 1)

    def test_create_invalid_payload_returns_422_and_saves_nothing(self):
        cases = {
            "empty-body": {},
            "too-short-username": {"username": "a", "email": "a@test.com"},
            "invalid-email": {"username": "matti", "email": "no-email"},
        }
        for case, payload in cases.items():
            with self.subTest(case=case):
                response = self.client.post(URL, json=payload)

                self.assertEqual(response.status_code, 422)
                self.assertEqual(self.get_saved_users(), [])

    def test_get_all_and_get_by_id(self):
        created = self.client.post(
            URL, json={"username": "mikko", "email": "mikko@test.com"}
        ).json()

        all_users = self.client.get(URL)
        self.assertEqual(all_users.status_code, 200)
        self.assertEqual(len(all_users.json()), 1)

        one_user = self.client.get(f"{URL}{created['id']}")
        self.assertEqual(one_user.status_code, 200)
        self.assertEqual(one_user.json()["username"], "mikko")

        missing_user = self.client.get(f"{URL}999")
        self.assertEqual(missing_user.status_code, 404)

    def test_update_modifies_user_in_database(self):
        created = self.client.post(
            URL, json={"username": "matti", "email": "matti@test.com"}
        ).json()

        response = self.client.patch(
            f"{URL}{created['id']}", json={"username": "matti_new"}
        )

        self.assertEqual(response.status_code, 200)
        self.session.expire_all()
        saved = self.get_saved_users()
        self.assertEqual(saved[0].username, "matti_new")

    def test_delete_removes_user_from_database(self):
        created = self.client.post(
            URL, json={"username": "matti", "email": "matti@test.com"}
        ).json()

        response = self.client.delete(f"{URL}{created['id']}")

        self.assertEqual(response.status_code, 204)
        self.session.expire_all()
        self.assertEqual(self.get_saved_users(), [])