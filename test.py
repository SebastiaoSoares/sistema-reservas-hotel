from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.main import app
from datetime import date, timedelta
import pytest

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_hotel.db"

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

# resetar banco antes dos testes
@pytest.fixture(scope="module", autouse=True)
def setup_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine) # limpar dados no final

def test_root():
    response = client.get("/")
    assert response.status_code == 200


# quartos

def test_criar_quarto():
    payload = {
        "number": 101,
        "type": "SIMPLES",
        "capacity": 2,
        "basic_fare": 100.0
    }
    response = client.post("/quartos/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["number"] == 101
    assert data["status"] == "DISPONIVEL"

def test_criar_quarto_duplicado():
    payload = {
        "number": 101,
        "type": "LUXO",
        "capacity": 2,
        "basic_fare": 200.0
    }
    response = client.post("/quartos/", json=payload)
    assert response.status_code == 400


# hospedes

def test_criar_hospede():
    payload = {
        "name": "João Silva",
        "email": "joao@email.com",
        "phone": "8899999999"
    }
    response = client.post("/hospedes/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "joao@email.com"


# reservas

def test_criar_reserva_sucesso():
    check_in = str(date.today() + timedelta(days=1))
    check_out = str(date.today() + timedelta(days=3))
    
    payload = {
        "guest_id": 1,
        "room_id": 1,
        "check_in": check_in,
        "check_out": check_out,
        "n_guests": 1
    }
    response = client.post("/reservas/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "CONFIRMADA"

def test_criar_reserva_conflito():
    # tentar reservar o mesmo quarto nas mesmas datas
    check_in = str(date.today() + timedelta(days=1))
    check_out = str(date.today() + timedelta(days=3))
    
    payload = {
        "guest_id": 1,
        "room_id": 1,
        "check_in": check_in,
        "check_out": check_out,
        "n_guests": 1
    }
    response = client.post("/reservas/", json=payload)
    assert response.status_code == 400
    assert "indisponível" in response.json()["detail"]


# fluxo: chekin, adicional, checkout

def test_fluxo_hospedagem():
    check_in = str(date.today())
    check_out = str(date.today() + timedelta(days=1))
    
    client.post("/quartos/", json={"number": 202, "type": "LUXO", "capacity": 2, "basic_fare": 200.0})
    
    res_payload = {
        "guest_id": 1,
        "room_id": 2,
        "check_in": check_in,
        "check_out": check_out,
        "n_guests": 1
    }
    res_response = client.post("/reservas/", json=res_payload)
    assert res_response.status_code == 201
    res_id = res_response.json()["id"]

    checkin_response = client.post(f"/reservas/{res_id}/checkin")
    assert checkin_response.status_code == 200
    assert checkin_response.json()["status"] == "CHECKIN"

    add_payload = {"description": "Frigobar", "value": 50.0}
    add_response = client.post(f"/reservas/{res_id}/adicionais", json=add_payload)
    assert add_response.status_code == 200

    checkout_response = client.post(f"/reservas/{res_id}/checkout")
    assert checkout_response.status_code == 200
    resumo = checkout_response.json()["resumo"]
    
    assert resumo["valor_adicionais"] == 50.0
    assert resumo["total_final"] > 50.0


# relatorios

def test_relatorios():
    start = str(date.today() - timedelta(days=5))
    end = str(date.today() + timedelta(days=30))
    
    response = client.get(f"/relatorios/geral?start_date={start}&end_date={end}")
    assert response.status_code == 200
    data = response.json()
    
    assert "metricas" in data
    assert "ocupacao_percentual" in data["metricas"]
    assert "adr" in data["metricas"]
    assert "revpar" in data["metricas"]