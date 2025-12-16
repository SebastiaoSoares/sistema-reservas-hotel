import pytest
from datetime import date, timedelta
from app.models import Room, Guest, Reservation, TypeRoom, StatusRoom, TypeDocument, Document

def test_validar_capacidade_quarto():
    """Valida erro ao criar quarto com capacidade <= 0."""
    with pytest.raises(ValueError) as excinfo:
        Room(number=101, type=TypeRoom.SIMPLE, capacity=0, basic_fare=100.0)
    assert "Capacidade deve ser >= 1" in str(excinfo.value)

def test_validar_tarifa_quarto():
    """Valida erro ao criar quarto com tarifa <= 0."""
    with pytest.raises(ValueError) as excinfo:
        Room(number=102, type=TypeRoom.SIMPLE, capacity=1, basic_fare=-50.0)
    assert "Tarifa deve ser > 0" in str(excinfo.value)

def test_validar_minimo_hospedes_reserva():
    """Valida erro ao criar reserva com 0 hóspedes."""
    with pytest.raises(ValueError) as excinfo:
        Reservation(n_guests=0, check_in=date.today(), check_out=date.today())
    assert "Mínimo 1 hóspede" in str(excinfo.value)

def test_heranca_guest_person():
    """Verifica herança de atributos de Person em Guest."""
    guest = Guest(name="João Teste", email="joao@test.com", phone="123456789")
    assert hasattr(guest, 'name')
    assert guest.name == "João Teste"
    assert str(guest) == "João Teste"

def test_composicao_documentos():
    """Testa relação entre Guest e Document."""
    doc = Document(type=TypeDocument.CPF, number="123.456.789-00")
    guest = Guest(name="Maria", documents=[doc])
    assert len(guest.documents) == 1
    assert guest.documents[0].number == "123.456.789-00"
    assert str(guest.documents[0]) == "CPF: 123.456.789-00"

def test_ordenacao_quartos_lt():
    """Testa ordenação (__lt__) por tipo e número."""
    q1 = Room(number=100, type=TypeRoom.DOUBLE)
    q2 = Room(number=200, type=TypeRoom.LUXURY)
    q3 = Room(number=300, type=TypeRoom.SIMPLE)
    q4 = Room(number=50, type=TypeRoom.SIMPLE)

    assert q1 < q2
    assert q2 < q3
    assert q4 < q3

def test_duracao_reserva_len():
    """Testa cálculo de diárias (__len__)."""
    check_in = date(2025, 12, 1)
    check_out = date(2025, 12, 5)
    res = Reservation(check_in=check_in, check_out=check_out)
    assert len(res) == 4

def test_igualdade_reserva_eq():
    """Testa igualdade (__eq__) de reservas."""
    d_in = date(2025, 1, 1)
    d_out = date(2025, 1, 5)
    res1 = Reservation(room_id=1, check_in=d_in, check_out=d_out)
    res2 = Reservation(room_id=1, check_in=d_in, check_out=d_out)
    res3 = Reservation(room_id=2, check_in=d_in, check_out=d_out)
    assert res1 == res2
    assert res1 != res3

def test_str_representacao():
    """Testa __str__ das classes."""
    q = Room(number=505, type=TypeRoom.LUXURY, capacity=2)
    assert str(q) == "Quarto 505 (LUXO)"