from pydantic import BaseModel
from datetime import date
from typing import List, Optional
from app.models import TypeRoom, StatusRoom, StatusReservation, TypeDocument

# --- Documentos ---
class DocumentCreate(BaseModel):
    type: TypeDocument
    number: str

class DocumentResponse(DocumentCreate):
    id: int
    class Config:
        from_attributes = True

# --- Quartos ---
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

# --- Hóspedes ---
class GuestCreate(BaseModel):
    name: str
    email: str
    phone: str
    documents: List[DocumentCreate] = []

class GuestResponse(GuestCreate):
    id: int
    documents: List[DocumentResponse]
    class Config:
        from_attributes = True

# --- Reservas & Financeiro ---
class PaymentCreate(BaseModel):
    method: str
    value: float

class AdditionalCreate(BaseModel):
    description: str
    value: float

class AdditionalResponse(AdditionalCreate):
    id: int
    reservation_id: int
    class Config:
        from_attributes = True

class ReservationCreate(BaseModel):
    guest_id: int
    room_id: int
    check_in: date
    check_out: date
    n_guests: int

class ReservationResponse(BaseModel):
    id: int
    check_in: date
    check_out: date
    status: StatusReservation
    room_id: int
    guest_id: int
    
    class Config:
        from_attributes = True