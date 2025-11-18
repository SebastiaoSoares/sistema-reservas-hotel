from fastapi import FastAPI
from app.models import Room, Guest, Reservation

app = FastAPI(
    title="Sistema de Reservas de Hotel",
    description="API para gerenciamento de hotel (Projeto 1 - POO)",
    version="1.0.0"
)

# --- Rotas teste ---

@app.get("/")
def read_root():
    """Rota teste."""
    return {"mensagem": "Sistema de Hotel rodando!", "status": "OK"}

@app.get("/quartos")
def list_rooms():
    """
    Retorna a lista de quartos.
    """
    return [{"quarto": 101, "status": "Disponível"}]

@app.post("/reservar")
def create_reservation(dados: dict):
    """
    Criar uma reserva.
    """
    return {"mensagem": "Reserva criada (simulação)", "dados_recebidos": dados}