import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from custom_exceptions.not_found_exception import NotFoundException
from db import Base
from dtos.users import CreateUserReq, UpdateUserReq
from services.user_service import UserService


class UserServiceTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.session = sessionmaker(bind=self.engine)()
        self.service = UserService(self.session)

    def tearDown(self):
        self.session.close()
        self.engine.dispose()

    def test_create_returns_user_with_id(self):
        created = self.service.create(
            CreateUserReq(username="matti", email="matti@test.com")
        )

        self.assertIsNotNone(created.id)
        self.assertEqual("matti", created.username)

    def test_get_all_returns_all_users(self):
        self.service.create(CreateUserReq(username="matti", email="matti@test.com"))
        self.service.create(CreateUserReq(username="mikko", email="mikko@test.com"))

        usernames = [u.username for u in self.service.get_all()]

        self.assertCountEqual(["matti", "mikko"], usernames)

    def test_get_by_id_returns_user(self):
        created = self.service.create(
            CreateUserReq(username="matti", email="matti@test.com")
        )

        found = self.service.get_by_id(created.id)

        self.assertEqual("matti", found.username)

    def test_get_by_id_unknown_raises_not_found(self):
        with self.assertRaises(NotFoundException):
            self.service.get_by_id(999)

    def test_update_changes_user_fields(self):
        created = self.service.create(
            CreateUserReq(username="matti", email="matti@test.com")
        )

        updated = self.service.update(
            created.id, UpdateUserReq(username="matti_new")
        )

        self.assertEqual("matti_new", updated.username)

    def test_delete_removes_user(self):
        created = self.service.create(
            CreateUserReq(username="matti", email="matti@test.com")
        )

        self.service.delete(created.id)

        with self.assertRaises(NotFoundException):
            self.service.get_by_id(created.id)


if __name__ == "__main__":
    unittest.main()