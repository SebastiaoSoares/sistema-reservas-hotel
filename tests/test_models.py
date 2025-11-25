import pytest
from datetime import date
from app.models import (Room, TypeRoom, Guest, TypeDocument, Reservation, StatusReservation)

def test_room_validation():
    """Testa validação de capacidade e tarifa."""
    room = Room(101, TypeRoom.SIMPLE, 2, 100.0)

    assert room.capacity == 2
    assert room.basic_fare == 100.0

    with pytest.raises(ValueError):
        room.capacity = 0

    with pytest.raises(ValueError):
        room.basic_fare = -50.0

def test_guest_document():
    """Testa adição de documentos ao hóspede."""
    guest = Guest("Jayr Alencar", "jayr@test.com", "1234-5678")
    guest.add_document(TypeDocument.CPF, "111.222.333-44")

    assert len(guest.documents) == 1
    assert guest.documents[0].number == "111.222.333-44"

def test_reservation_success():
    """Testa fluxo normal de reserva."""
    guest = Guest("Sebastião", "sebastiao@test.com", "8765-4321")
    room = Room(202, TypeRoom.LUXURY, 3, 500.0)

    check_in = date(2024, 12, 20)
    check_out = date(2024, 12, 25)

    reservation = Reservation(guest, room, check_in, check_out, 3)

    assert len(reservation) == 5
    assert reservation.status == StatusReservation.PENDING

def test_reservation_errors():
    """Testa validações de data e capacidade."""

    guest = Guest("Will", "will@test.com", "0000-0000")
    room = Room(303, TypeRoom.SIMPLE, 1, 150.0)

    with pytest.raises(ValueError):
        Reservation(guest, room, date(2024, 1, 10), date(2024, 1, 10), 1)

    with pytest.raises(ValueError):
        Reservation(guest, room, date(2024, 1, 1), date(2024, 1, 2), 2)