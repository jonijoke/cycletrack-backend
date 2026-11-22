from sqlalchemy.orm import Session

import models
from custom_exceptions.conflict_exception import ConflictException
from custom_exceptions.not_found_exception import NotFoundException
from dtos.users import CreateUserReq, UpdateUserReq
from services.abc_user_service import ABCUserService


class UserService(ABCUserService):
    def __init__(self, _repository: Session):
        self._repository = _repository

    def get_all(self) -> list[models.User]:
        return self._repository.query(models.User).all()

    def get_by_id(self, _id: int) -> models.User:
        user = self._repository.query(models.User).filter_by(id=_id).first()
        if user is None:
            raise NotFoundException(f"user {_id} not found")
        return user

    def create(self, req: CreateUserReq) -> models.User:
        if (
            self._repository.query(models.User).filter_by(username=req.username).first()
            is not None
        ):
            raise ConflictException(f"username {req.username} already exists")

        if (
            self._repository.query(models.User).filter_by(email=req.email).first()
            is not None
        ):
            raise ConflictException(f"email {req.email} already exists")

        user = models.User(username=req.username, email=req.email)
        self._repository.add(user)
        self._repository.commit()
        return user

    def update(self, _id: int, req: UpdateUserReq) -> models.User:
        user = self.get_by_id(_id)

        if req.username is not None and req.username != user.username:
            if (
                self._repository.query(models.User)
                .filter_by(username=req.username)
                .first()
                is not None
            ):
                raise ConflictException(f"username {req.username} already exists")
            user.username = req.username

        if req.email is not None and req.email != user.email:
            if (
                self._repository.query(models.User).filter_by(email=req.email).first()
                is not None
            ):
                raise ConflictException(f"email {req.email} already exists")
            user.email = req.email

        self._repository.commit()
        return user

    def delete(self, _id: int) -> None:
        user = self.get_by_id(_id)
        self._repository.delete(user)
        self._repository.commit()
