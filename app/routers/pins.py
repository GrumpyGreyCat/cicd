from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.schemas import PinCreate, PinOut, PinUpdate
from app.storage import JsonStorage, get_storage

router = APIRouter(prefix="/api/v1/pins", tags=["pins"])
Storage = Annotated[JsonStorage, Depends(get_storage)]


@router.post("/", response_model=PinOut, status_code=status.HTTP_201_CREATED)
def create_pin(payload: PinCreate, storage: Storage):
    if storage.get_user_by_id(payload.user_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
    return storage.save_pin(payload.model_dump())


@router.get("/", response_model=list[PinOut])
def list_pins(storage: Storage):
    return storage.get_pins()


@router.get("/{pin_id}", response_model=PinOut)
def get_pin(pin_id: int, storage: Storage):
    pin = storage.get_pin_by_id(pin_id)
    if pin is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Pin not found")
    return pin


@router.put("/{pin_id}", response_model=PinOut)
def update_pin(pin_id: int, payload: PinUpdate, storage: Storage):
    pin = storage.update_pin(pin_id, payload.model_dump(exclude_unset=True))
    if pin is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Pin not found")
    return pin


@router.delete("/{pin_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_pin(pin_id: int, storage: Storage):
    if not storage.delete_pin(pin_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Pin not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
