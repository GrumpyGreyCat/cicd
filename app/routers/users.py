from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.schemas import UserCreate, UserOut, UserUpdate
from app.storage import JsonStorage, get_storage

router = APIRouter(prefix="/api/v1/users", tags=["users"])
Storage = Annotated[JsonStorage, Depends(get_storage)]


def _check_unique(storage: JsonStorage, username: str | None, email: str | None, user_id=None):
    for u in storage.get_users():
        if u["id"] == user_id:
            continue
        if (email and u["email"].lower() == email.lower()) or (
            username and u["username"].lower() == username.lower()
        ):
            raise HTTPException(status.HTTP_409_CONFLICT, "Username or email already used")


@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, storage: Storage):
    _check_unique(storage, payload.username, payload.email)
    return storage.save_user(payload.model_dump())


@router.get("/", response_model=list[UserOut])
def list_users(storage: Storage):
    return storage.get_users()


@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: int, storage: Storage):
    user = storage.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
    return user


@router.put("/{user_id}", response_model=UserOut)
def update_user(user_id: int, payload: UserUpdate, storage: Storage):
    if storage.get_user_by_id(user_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
    fields = payload.model_dump(exclude_unset=True)
    _check_unique(storage, fields.get("username"), fields.get("email"), user_id)
    return storage.update_user(user_id, fields)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, storage: Storage):
    if not storage.delete_user(user_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
