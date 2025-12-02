from fastapi import FastAPI
from app.database import engine, Base
from app.routers import quartos, reservas, hospedes

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Sistema de Reservas de Hotel")

app.include_router(quartos.router, prefix="/quartos", tags=["Quartos"])
app.include_router(hospedes.router, prefix="/hospedes", tags=["Hóspedes"])
app.include_router(reservas.router, prefix="/reservas", tags=["Reservas"])
