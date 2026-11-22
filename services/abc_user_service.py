import abc

import models
from dtos.users import CreateUserReq, UpdateUserReq


class ABCUserService(abc.ABC):
    @abc.abstractmethod
    def get_all(self) -> list[models.User]:
        raise NotImplementedError()  # pragma: no cover

    @abc.abstractmethod
    def get_by_id(self, _id: int) -> models.User:
        raise NotImplementedError()  # pragma: no cover

    @abc.abstractmethod
    def create(self, req: CreateUserReq) -> models.User:
        raise NotImplementedError()  # pragma: no cover

    @abc.abstractmethod
    def update(self, _id: int, req: UpdateUserReq) -> models.User:
        raise NotImplementedError()  # pragma: no cover

    @abc.abstractmethod
    def delete(self, _id: int) -> None:
        raise NotImplementedError()  # pragma: no cover
