from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.main import app
from datetime import date, timedelta
import pytest

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_hotel_flow.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_criar_entidades_basicas():
    """Cria quarto e hóspede iniciais."""
    client.post("/quartos/", json={
        "number": 101, "type": "SIMPLES", "capacity": 2, "basic_fare": 100.0
    })
    client.post("/hospedes/", json={
        "name": "Teste Flow", "email": "flow@test.com", "phone": "00000000"
    })

def test_impedir_overbooking():
    """Valida erro ao reservar período ocupado."""
    c_in = str(date.today())
    c_out = str(date.today() + timedelta(days=2))
    
    res1 = client.post("/reservas/", json={
        "guest_id": 1, "room_id": 1, "check_in": c_in, "check_out": c_out, "n_guests": 1
    })
    assert res1.status_code == 201
    
    res2 = client.post("/reservas/", json={
        "guest_id": 1, "room_id": 1, "check_in": c_in, "check_out": c_out, "n_guests": 1
    })
    assert res2.status_code == 400
    assert "indisponível" in res2.json()["detail"]

def test_validar_capacidade_excedida_api():
    """Valida erro se hóspedes > capacidade."""
    res = client.post("/reservas/", json={
        "guest_id": 1, "room_id": 1, 
        "check_in": str(date.today() + timedelta(days=10)), 
        "check_out": str(date.today() + timedelta(days=12)), 
        "n_guests": 5
    })
    assert res.status_code == 400
    assert "Capacidade do quarto excedida" in res.json()["detail"]

def test_fluxo_checkin_checkout_pagamento():
    """Testa fluxo completo: Reserva, Checkin, Adicional, Checkout."""
    c_in = str(date.today() + timedelta(days=5))
    c_out = str(date.today() + timedelta(days=7))
    
    r = client.post("/reservas/", json={
        "guest_id": 1, "room_id": 1, "check_in": c_in, "check_out": c_out, "n_guests": 1
    })
    assert r.status_code == 201
    res_id = r.json()["id"]

    checkin = client.post(f"/reservas/{res_id}/checkin")
    assert checkin.status_code == 200
    assert checkin.json()["status"] == "CHECKIN"

    client.post(f"/reservas/{res_id}/adicionais", json={"description": "Serviço", "value": 50.0})

    checkout = client.post(f"/reservas/{res_id}/checkout")
    assert checkout.status_code == 200
    data = checkout.json()["resumo"]
    
    assert data["valor_adicionais"] == 50.0
    assert data["total_final"] >= 250.0 

def test_cancelamento_reserva():
    """Testa cancelamento e liberação do quarto."""
    c_in = str(date.today() + timedelta(days=20))
    c_out = str(date.today() + timedelta(days=21))
    
    r = client.post("/reservas/", json={
        "guest_id": 1, "room_id": 1, "check_in": c_in, "check_out": c_out, "n_guests": 1
    })
    res_id = r.json()["id"]
    
    cancel = client.post(f"/reservas/{res_id}/cancel")
    assert cancel.status_code == 200
    
    r2 = client.post("/reservas/", json={
        "guest_id": 1, "room_id": 1, "check_in": c_in, "check_out": c_out, "n_guests": 1
    })
    assert r2.status_code == 201

def test_relatorios_metricas():
    """Valida chaves do relatório."""
    start = str(date.today())
    end = str(date.today() + timedelta(days=30))
    
    resp = client.get(f"/relatorios/geral?start_date={start}&end_date={end}")
    assert resp.status_code == 200
    data = resp.json()
    
    assert "taxa_ocupacao_percentual" in data["metricas"]
    assert "revpar" in data["metricas"]
    assert "adr" in data["metricas"]