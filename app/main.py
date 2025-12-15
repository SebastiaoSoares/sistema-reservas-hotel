from fastapi import FastAPI
from app.database import engine, Base
from app.routers import quartos, reservas, hospedes, relatorios

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Sistema de Reservas de Hotel",
    description="API para gerenciamento de hotel (Projeto POO - UFCA)",
    version="1.0.0"
)

app.include_router(quartos.router, prefix="/quartos", tags=["Quartos"])
app.include_router(hospedes.router, prefix="/hospedes", tags=["Hóspedes"])
app.include_router(reservas.router, prefix="/reservas", tags=["Reservas"])
app.include_router(relatorios.router, prefix="/relatorios", tags=["Relatórios"])

@app.get("/")
def root():
    return {"message": "API ok! Acesse /docs para documentação."}
