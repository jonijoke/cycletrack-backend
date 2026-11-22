from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

import dtos.users
from custom_exceptions.conflict_exception import ConflictException
from custom_exceptions.not_found_exception import NotFoundException
from factories.services import user_service_factory
from services.abc_user_service import ABCUserService

router = APIRouter(prefix="/api/users", tags=["users"])

UserServ = Annotated[ABCUserService, Depends(user_service_factory)]


@router.get("/")
def get_all(_service: UserServ) -> list[dtos.users.UserDto]:
    return _service.get_all()


@router.get("/{user_id}")
def get_by_id(user_id: int, _service: UserServ) -> dtos.users.UserDto:
    try:
        return _service.get_by_id(user_id)
    except NotFoundException as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error))


@router.post("/", status_code=status.HTTP_201_CREATED)
def create(req: dtos.users.CreateUserReq, _service: UserServ) -> dtos.users.UserDto:
    try:
        return _service.create(req)
    except ConflictException as error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error))


@router.patch("/{user_id}")
def update(
    user_id: int, req: dtos.users.UpdateUserReq, _service: UserServ
) -> dtos.users.UserDto:
    try:
        return _service.update(user_id, req)
    except NotFoundException as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error))
    except ConflictException as error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error))


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(user_id: int, _service: UserServ):
    try:
        _service.delete(user_id)
    except NotFoundException as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error))
