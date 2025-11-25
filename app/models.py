"""
Definição das classes principais do sistema de reservas de hotel.
"""

from datetime import date
from enum import Enum
from typing import List

# Enums para tipos e status

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
    PASSPORT = "Passaporte"

# Classes principais

class Person:
    """
    Classe base que representa uma Pessoa.
    """
    def __init__(self, name: str, email: str, phone: str):
        self.name = name
        self.email = email
        self.phone = phone
        self.documents: List['Document'] = []

    def add_document(self, type_doc: TypeDocument, number: str):
        document = Document(type_doc, number)
        self.documents.append(document)

    def __str__(self):
        return self.name

class Document:
    """
    Representa um documento de identificação.
    """
    def __init__(self, doc_type: TypeDocument, number: str):
        self.doc_type = doc_type
        self.number = number

    def __str__(self):
        return f"{self.number} ({self.doc_type.value})"

class Guest(Person):
    """
    Classe Hospede, herda de Pessoa e armazena o histórico de reservas.
    """
    def __init__(self, name: str, email: str, phone: str):
        super().__init__(name, email, phone)
        self.history: List['Reservation'] = []

class Room:
    """
    Dados referentes aos quartos do hotel.
    """
    def __init__(self, number: int, room_type: TypeRoom, capacity: int, basic_fare: float):
        self.number = number
        self.type = room_type
        self._capacity = 0
        self.capacity = capacity
        self._basic_fare = 0.0
        self.basic_fare = basic_fare
        self.status = StatusRoom.AVAILABLE

    @property
    def capacity(self):
        return self._capacity

    @capacity.setter
    def capacity(self, value: int):
        if value < 1:
            raise ValueError("Capacity must be at least 1.")
        self._capacity = value

    @property
    def basic_fare(self):
        return self._basic_fare

    @basic_fare.setter
    def basic_fare(self, value: float):
        if value <= 0:
            raise ValueError("Basic fare must be greater than zero.")
        self._basic_fare = value

    def __str__(self):
        return f"Room {self.number} ({self.type.value}) - Cap: {self.capacity}"
    
    def __lt__(self, other):
        if not isinstance(other, Room):
            return NotImplemented
        if self.type.value != other.type.value:
            return self.type.value < other.type.value
        return self.number < other.number

class Additional:
    """
    Representa um item de consumo ou serviço extra.
    """
    def __init__(self, description: str, value: float):
        self.description = description
        self.value = value

class Payment:
    """
    Representa uma transação financeira.
    """
    def __init__(self, method: str, value: float):
        self.method = method
        self.value = value
        self.date = date.today()

class Reservation:
    """
    Representa o contrato de locação entre um Hospede e um Quarto.
    """
    def __init__(self, guest: Guest, room: Room, check_in: date, check_out: date, n_guests: int):
        self.guest = guest
        self.room = room
        
        if check_in >= check_out:
            raise ValueError("Check-in date must be before check-out date.")
        self.check_in = check_in
        self.check_out = check_out

        if n_guests > room.capacity:
            raise ValueError(f"Guests ({n_guests}) exceed room capacity ({room.capacity}).")
        self.n_guests = n_guests

        self.status = StatusReservation.PENDING
        self.payments: List[Payment] = []
        self.additionals: List[Additional] = []

    def __len__(self):
        """Retorna o número de diárias."""
        return (self.check_out - self.check_in).days

    def __eq__(self, other):
        """Verifica igualdade baseada no quarto e intervalo de datas."""
        if not isinstance(other, Reservation):
            return False
        return (self.room.number == other.room.number and
                self.check_in == other.check_in and
                self.check_out == other.check_out)

    def __str__(self):
        return f"Res: {self.guest.name} - Room {self.room.number} ({self.status.value})"
