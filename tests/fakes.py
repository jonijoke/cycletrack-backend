import models
from dtos.users import CreateUserReq, UpdateUserReq
from services.abc_user_service import ABCUserService


class FakeUserService(ABCUserService):
    def __init__(
        self,
        users: list[models.User] = None,
        raises: Exception = None,
    ):
        self._users = users or []
        self._raises = raises

    def get_all(self) -> list[models.User]:
        return self._users

    def get_by_id(self, _id: int) -> models.User:
        if self._raises:
            raise self._raises
        return self._users[0]

    def create(self, req: CreateUserReq) -> models.User:
        if self._raises:
            raise self._raises
        return models.User(id=1, username=req.username, email=req.email)

    def update(self, _id: int, req: UpdateUserReq) -> models.User:
        if self._raises:
            raise self._raises
        return models.User(
            id=_id,
            username=req.username or "testname",
            email=req.email or "test@test.com",
        )

    def delete(self, _id: int) -> None:
        if self._raises:
            raise self._raises