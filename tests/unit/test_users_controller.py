import unittest

from fastapi.testclient import TestClient

import models
from custom_exceptions.conflict_exception import ConflictException
from custom_exceptions.not_found_exception import NotFoundException
from factories.services import user_service_factory
from main import app
from tests.fakes import FakeUserService


class UsersControllerTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def tearDown(self):
        app.dependency_overrides.clear()

    def test_get_all_returns_200_and_users(self):
        app.dependency_overrides[user_service_factory] = lambda: FakeUserService(
            users=[models.User(id=1, username="matti", email="matti@test.com")]
        )

        response = self.client.get("/api/users/")

        self.assertEqual(200, response.status_code)
        self.assertEqual(1, len(response.json()))
        self.assertEqual("matti", response.json()[0]["username"])

    def test_get_by_id_not_found_returns_404(self):
        app.dependency_overrides[user_service_factory] = lambda: FakeUserService(
            raises=NotFoundException("user 42 not found")
        )

        response = self.client.get("/api/users/42")

        self.assertEqual(404, response.status_code)

    def test_create_returns_201(self):
        app.dependency_overrides[user_service_factory] = lambda: FakeUserService()

        response = self.client.post(
            "/api/users/",
            json={"username": "mikko", "email": "mikko@test.com"},
        )

        self.assertEqual(201, response.status_code)
        self.assertEqual("mikko", response.json()["username"])

    def test_create_duplicate_returns_409(self):
        app.dependency_overrides[user_service_factory] = lambda: FakeUserService(
            raises=ConflictException("email already exists")
        )

        response = self.client.post(
            "/api/users/",
            json={"username": "mikko", "email": "mikko@test.com"},
        )

        self.assertEqual(409, response.status_code)

    def test_create_invalid_payload_returns_422(self):
        app.dependency_overrides[user_service_factory] = lambda: FakeUserService()

        response = self.client.post("/api/users/", json={"username": ""})

        self.assertEqual(422, response.status_code)

    def test_update_returns_200(self):
        app.dependency_overrides[user_service_factory] = lambda: FakeUserService()

        response = self.client.patch(
            "/api/users/1",
            json={"username": "mikko_new"},
        )

        self.assertEqual(200, response.status_code)
        self.assertEqual("mikko_new", response.json()["username"])

    def test_delete_returns_204(self):
        app.dependency_overrides[user_service_factory] = lambda: FakeUserService()

        response = self.client.delete("/api/users/1")

        self.assertEqual(204, response.status_code)


if __name__ == "__main__":
    unittest.main()