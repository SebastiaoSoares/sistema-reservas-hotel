from pydantic import BaseModel
from datetime import date
from typing import List, Optional
from app.models import TypeRoom, StatusRoom, StatusReservation

class RoomCreate(BaseModel):
    number: int
    type: TypeRoom
    capacity: int
    basic_fare: float

class RoomResponse(RoomCreate):
    id: int
    status: StatusRoom
    class Config:
        from_attributes = True

class ReservationCreate(BaseModel):
    guest_id: int
    room_id: int
    check_in: date
    check_out: date
    n_guests: int

class PaymentCreate(BaseModel):
    method: str
    value: float

class AdditionalCreate(BaseModel):
    description: str
    value: float

class GuestCreate(BaseModel):
    name: str
    email: str
    phone: str

class GuestResponse(GuestCreate):
    id: int
    class Config:
        from_attributes = True