from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, settings
from datetime import date, timedelta
from typing import List, Dict, Any

router = APIRouter()

@router.get("/geral")
def gerar_relatorio_geral(start_date: date, end_date: date, db: Session = Depends(get_db)):
    """
    Relatórios entre duas datas:
    - Taxa de Ocupação (%)
    - ADR (Diária Média)
    - RevPAR (Receita por Quarto Disponível)
    - Contagem de Cancelamentos e No-Shows
    """
    
    if start_date >= end_date:
        raise HTTPException(status_code=400, detail="Data inicial deve ser anterior à final.")

    # obter dados base
    total_quartos = db.query(models.Room).count()
    if total_quartos == 0:
        return {"message": "Nenhum quarto cadastrado para gerar métricas."}

    # reservas que tocam o período solicitado (mesmo que parcialmente)
    reservas = db.query(models.Reservation).filter(
        models.Reservation.check_in < end_date,
        models.Reservation.check_out > start_date
    ).all()

    receita_hospedagem = 0.0
    room_nights_vendidas = 0
    total_dias_periodo = (end_date - start_date).days
    total_room_nights_disponiveis = total_quartos * total_dias_periodo

    # calculo dia a dia (para precisão de tarifas de fim de semana/temporada)
    current_date = start_date
    while current_date < end_date:
        
        for res in reservas:
            if res.status in [models.StatusReservation.CANCELED, models.StatusReservation.NO_SHOW]:
                continue
            
            if res.check_in <= current_date < res.check_out:
                diaria = res.room.basic_fare
                
                if current_date.weekday() >= 5:
                    diaria *= settings.SETTINGS["WEEKEND_MULTIPLIER"]
                
                if current_date.month in settings.SETTINGS["HIGH_SEASON_MONTHS"]:
                    diaria *= settings.SETTINGS["SEASON_MULTIPLIER"]
                
                receita_hospedagem += diaria
                room_nights_vendidas += 1
        
        current_date += timedelta(days=1)

    # contagem de ocorrências (cancelamentos e no-show)
    reservas_inicio_periodo = db.query(models.Reservation).filter(
        models.Reservation.check_in >= start_date,
        models.Reservation.check_in < end_date
    ).all()

    cancelamentos = sum(1 for r in reservas_inicio_periodo if r.status == models.StatusReservation.CANCELED)
    no_shows = sum(1 for r in reservas_inicio_periodo if r.status == models.StatusReservation.NO_SHOW)

    # Métricas Finais
    taxa_ocupacao = (room_nights_vendidas / total_room_nights_disponiveis) * 100 if total_room_nights_disponiveis > 0 else 0.0
    
    # ADR = Receita de Hospedagem / Quartos Vendidos
    adr = (receita_hospedagem / room_nights_vendidas) if room_nights_vendidas > 0 else 0.0
    
    # RevPAR = Receita de Hospedagem / Quartos Disponíveis (Total)
    revpar = (receita_hospedagem / total_room_nights_disponiveis) if total_room_nights_disponiveis > 0 else 0.0

    return {
        "periodo": {
            "inicio": start_date,
            "fim": end_date,
            "total_dias": total_dias_periodo
        },
        "metricas": {
            "receita_total_hospedagem": round(receita_hospedagem, 2),
            "room_nights_vendidas": room_nights_vendidas,
            "room_nights_disponiveis": total_room_nights_disponiveis,
            "taxa_ocupacao_percentual": round(taxa_ocupacao, 2),
            "adr": round(adr, 2),
            "revpar": round(revpar, 2)
        },
        "ocorrencias": {
            "cancelamentos": cancelamentos,
            "no_shows": no_shows
        }
    }