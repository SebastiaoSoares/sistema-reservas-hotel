from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.main import app
from app.settings import SETTINGS
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
    """cria base p/ testes"""
    # quarto 101 (p/ testes de erro)
    client.post("/quartos/", json={
        "number": 101, "type": "SIMPLES", "capacity": 2, "basic_fare": 100.0
    })
    # quarto 102 (p/ fluxo feliz)
    client.post("/quartos/", json={
        "number": 102, "type": "SIMPLES", "capacity": 2, "basic_fare": 100.0
    })
    
    # hospede
    client.post("/hospedes/", json={
        "name": "Teste Flow", "email": "flow@test.com", "phone": "00000000"
    })

def test_impedir_overbooking():
    """valida conflito de datas"""
    c_in = str(date.today())
    c_out = str(date.today() + timedelta(days=2))
    
    # reserva 1 - sucesso
    res1 = client.post("/reservas/", json={
        "guest_id": 1, "room_id": 1, "check_in": c_in, "check_out": c_out, "n_guests": 1
    })
    assert res1.status_code == 201
    
    # reserva 2 - falha (mesmo quarto/data)
    res2 = client.post("/reservas/", json={
        "guest_id": 1, "room_id": 1, "check_in": c_in, "check_out": c_out, "n_guests": 1
    })
    assert res2.status_code == 400
    assert "indisponível" in res2.json()["detail"]

def test_validar_capacidade_excedida_api():
    """valida limite de pessoas"""
    res = client.post("/reservas/", json={
        "guest_id": 1, "room_id": 1, 
        "check_in": str(date.today() + timedelta(days=10)), 
        "check_out": str(date.today() + timedelta(days=12)), 
        "n_guests": 5
    })
    assert res.status_code == 400
    assert "Capacidade do quarto excedida" in res.json()["detail"]

def test_fluxo_checkin_checkout_pagamento():
    """fluxo completo com calculo dinamico"""
    c_in = date.today()
    c_out = c_in + timedelta(days=2)
    
    # usa quarto 102
    r = client.post("/reservas/", json={
        "guest_id": 1, "room_id": 2, 
        "check_in": str(c_in), 
        "check_out": str(c_out), 
        "n_guests": 1
    })
    assert r.status_code == 201
    res_id = r.json()["id"]

    # checkin
    client.post(f"/reservas/{res_id}/checkin")

    # adicional
    val_add = 50.0
    client.post(f"/reservas/{res_id}/adicionais", json={"description": "Serviço", "value": val_add})

    # --- CALCULO DINAMICO ---
    # replica logica do backend p/ saber quanto pagar
    total_diarias = 0.0
    temp_date = c_in
    while temp_date < c_out:
        diaria = 100.0 # tarifa do quarto 102
        
        # regra fim de semana
        if temp_date.weekday() >= 5:
            diaria *= SETTINGS["WEEKEND_MULTIPLIER"]
            
        # regra alta temporada
        if temp_date.month in SETTINGS["HIGH_SEASON_MONTHS"]:
            diaria *= SETTINGS["SEASON_MULTIPLIER"]
            
        total_diarias += diaria
        temp_date += timedelta(days=1)
    
    total_devido = total_diarias + val_add
    
    # paga valor exato calculado
    client.post(f"/reservas/{res_id}/pagamentos", json={"method": "PIX", "value": total_devido})

    # checkout
    checkout = client.post(f"/reservas/{res_id}/checkout")
    assert checkout.status_code == 200
    
    data = checkout.json()["financeiro"]
    assert data["total_pago"] >= data["total_servicos"]

def test_cancelamento_reserva():
    """cancela e libera quarto"""
    c_in = str(date.today() + timedelta(days=20))
    c_out = str(date.today() + timedelta(days=21))
    
    # cria
    r = client.post("/reservas/", json={
        "guest_id": 1, "room_id": 1, "check_in": c_in, "check_out": c_out, "n_guests": 1
    })
    res_id = r.json()["id"]
    
    # cancela
    cancel = client.post(f"/reservas/{res_id}/cancel")
    assert cancel.status_code == 200
    
    # tenta reservar de novo
    r2 = client.post("/reservas/", json={
        "guest_id": 1, "room_id": 1, "check_in": c_in, "check_out": c_out, "n_guests": 1
    })
    assert r2.status_code == 201

def test_relatorios_metricas():
    """valida chaves do json"""
    start = str(date.today())
    end = str(date.today() + timedelta(days=30))
    
    resp = client.get(f"/relatorios/geral?start_date={start}&end_date={end}")
    assert resp.status_code == 200
    data = resp.json()
    
    assert "taxa_ocupacao_percentual" in data["metricas"]
    assert "revpar" in data["metricas"]
    assert "adr" in data["metricas"]