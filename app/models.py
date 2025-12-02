from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.database import Base
from enum import Enum
from datetime import date

class TypeRoom(str, Enum):
    SIMPLE = "SIMPLES"
    DOUBLE = "DUPLO"
    LUXURY = "LUXO"

class StatusRoom(str, Enum):
    AVAILABLE = "DISPONIVEL"
    OCCUPIED = "OCUPADO"
    MAINTENANCE = "MANUTENCAO"
    BLOCKED = "BLOQUEADO"

class StatusReservation(str, Enum):
    PENDING = "PENDENTE"
    CONFIRMED = "CONFIRMADA"
    CHECKIN = "CHECKIN"
    CHECKOUT = "CHECKOUT"
    CANCELED = "CANCELADA"
    NO_SHOW = "NO_SHOW"

class Room(Base):
    __tablename__ = "quartos"

    id = Column(Integer, primary_key=True, index=True)
    number = Column(Integer, unique=True, index=True)
    type = Column(SQLEnum(TypeRoom))
    capacity = Column(Integer)
    basic_fare = Column(Float)
    status = Column(SQLEnum(StatusRoom), default=StatusRoom.AVAILABLE)

    reservations = relationship("Reservation", back_populates="room")

    def __str__(self):
        return f"Quarto {self.number} ({self.type.value})"

class Guest(Base):
    __tablename__ = "hospedes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    phone = Column(String)
    
    reservations = relationship("Reservation", back_populates="guest")

class Reservation(Base):
    __tablename__ = "reservas"

    id = Column(Integer, primary_key=True, index=True)
    check_in = Column(Date)
    check_out = Column(Date)
    n_guests = Column(Integer)
    status = Column(SQLEnum(StatusReservation), default=StatusReservation.PENDING)
    
    guest_id = Column(Integer, ForeignKey("hospedes.id"))
    room_id = Column(Integer, ForeignKey("quartos.id"))

    guest = relationship("Guest", back_populates="reservations")
    room = relationship("Room", back_populates="reservations")
    payments = relationship("Payment", back_populates="reservation")
    additionals = relationship("Additional", back_populates="reservation")

    def __len__(self):
        """Retorna o número de diárias """
        return (self.check_out - self.check_in).days

class Payment(Base):
    """Lançamento de Pagamentos """
    __tablename__ = "pagamentos"

    id = Column(Integer, primary_key=True, index=True)
    method = Column(String)
    value = Column(Float)
    date = Column(Date, default=date.today)
    reservation_id = Column(Integer, ForeignKey("reservas.id"))

    reservation = relationship("Reservation", back_populates="payments")

class Additional(Base):
    """Lançamento de Adicionais """
    __tablename__ = "adicionais"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String)
    value = Column(Float)
    reservation_id = Column(Integer, ForeignKey("reservas.id"))

    reservation = relationship("Reservation", back_populates="additionals")
