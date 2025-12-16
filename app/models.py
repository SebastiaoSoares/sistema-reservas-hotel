from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship, validates
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

class TypeDocument(str, Enum):
    CPF = "CPF"
    PASSPORT = "PASSAPORTE"

class Person(Base):
    """Classe base abstrata para pessoas."""
    __abstract__ = True

    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
    phone = Column(String)

    def __str__(self):
        return self.name

class Document(Base):
    """Documentos de identificação."""
    __tablename__ = "documentos"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(SQLEnum(TypeDocument))
    number = Column(String)
    
    guest_id = Column(Integer, ForeignKey("hospedes.id"))
    guest = relationship("Guest", back_populates="documents")

    def __str__(self):
        return f"{self.type.value}: {self.number}"

class Guest(Person):
    """Entidade Hóspede herdando de Person."""
    __tablename__ = "hospedes"

    id = Column(Integer, primary_key=True, index=True)
    
    reservations = relationship("Reservation", back_populates="guest")
    documents = relationship("Document", back_populates="guest")

class Room(Base):
    """Entidade Quarto."""
    __tablename__ = "quartos"

    id = Column(Integer, primary_key=True, index=True)
    number = Column(Integer, unique=True, index=True)
    type = Column(SQLEnum(TypeRoom))
    capacity = Column(Integer)
    basic_fare = Column(Float)
    status = Column(SQLEnum(StatusRoom), default=StatusRoom.AVAILABLE)

    reservations = relationship("Reservation", back_populates="room")

    @validates('capacity')
    def validate_capacity(self, key, value):
        if value < 1:
            raise ValueError("Capacidade deve ser >= 1")
        return value

    @validates('basic_fare')
    def validate_fare(self, key, value):
        if value <= 0:
            raise ValueError("Tarifa deve ser > 0")
        return value

    def __str__(self):
        return f"Quarto {self.number} ({self.type.value})"

    def __lt__(self, other):
        if not isinstance(other, Room):
            return NotImplemented
        if self.type != other.type:
            return self.type.value < other.type.value
        return self.number < other.number

class Reservation(Base):
    """Entidade Reserva."""
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

    @validates('n_guests')
    def validate_guests(self, key, value):
        if value < 1:
            raise ValueError("Mínimo 1 hóspede")
        return value

    def __len__(self):
        if self.check_in and self.check_out:
            delta = (self.check_out - self.check_in).days
            return max(delta, 0)
        return 0

    def __eq__(self, other):
        if isinstance(other, Reservation):
            return (self.room_id == other.room_id and 
                    self.check_in == other.check_in and 
                    self.check_out == other.check_out)
        return False
    
    def __str__(self):
        return f"Reserva {self.id}: {self.guest.name if self.guest else 'Guest'} -> Quarto {self.room_id}"

class Payment(Base):
    """Lançamento de Pagamentos."""
    __tablename__ = "pagamentos"

    id = Column(Integer, primary_key=True, index=True)
    method = Column(String)
    value = Column(Float)
    date = Column(Date, default=date.today)
    reservation_id = Column(Integer, ForeignKey("reservas.id"))

    reservation = relationship("Reservation", back_populates="payments")

class Additional(Base):
    """Lançamento de Adicionais."""
    __tablename__ = "adicionais"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String)
    value = Column(Float)
    reservation_id = Column(Integer, ForeignKey("reservas.id"))

    reservation = relationship("Reservation", back_populates="additionals")