from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app import models, schemas
from datetime import date

router = APIRouter()

@router.post("/", response_model=schemas.ReservationCreate)
def create_reservation(res: schemas.ReservationCreate, db: Session = Depends(get_db)):
    room = db.query(models.Room).filter(models.Room.id == res.room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Quarto não encontrado")
    
    if res.n_guests > room.capacity:
        raise HTTPException(status_code=400, detail="Capacidade excedida")

    if res.check_in >= res.check_out:
        raise HTTPException(status_code=400, detail="Data de check-in deve ser anterior ao check-out")

    new_res = models.Reservation(**res.dict())
    db.add(new_res)
    db.commit()
    db.refresh(new_res)
    return new_res

@router.post("/{res_id}/pagamentos")
def add_payment(res_id: int, pay: schemas.PaymentCreate, db: Session = Depends(get_db)):
    payment = models.Payment(**pay.dict(), reservation_id=res_id)
    db.add(payment)
    db.commit()
    return {"message": "Pagamento registrado"}

@router.post("/{res_id}/adicionais")
def add_additional(res_id: int, add: schemas.AdditionalCreate, db: Session = Depends(get_db)):
    additional = models.Additional(**add.dict(), reservation_id=res_id)
    db.add(additional)
    db.commit()
    return {"message": "Adicional registrado"}

@router.get("/relatorio/ocupacao")
def occupation_report(start: date, end: date, db: Session = Depends(get_db)):
    """
    Calcula taxa de ocupação por período (%).
    Fórmula simples: Dias ocupados / (Total de quartos * Dias no período)
    """
    total_rooms = db.query(models.Room).count()
    if total_rooms == 0:
        return {"ocupacao": 0}

    reservations = db.query(models.Reservation).filter(
        models.Reservation.check_in < end,
        models.Reservation.check_out > start,
        models.Reservation.status.in_([models.StatusReservation.CONFIRMED, models.StatusReservation.CHECKIN])
    ).all()

    total_days_period = (end - start).days
    occupied_days = 0

    for res in reservations:
        max_start = max(res.check_in, start)
        min_end = min(res.check_out, end)
        days = (min_end - max_start).days
        occupied_days += days

    capacity_days = total_rooms * total_days_period
    rate = (occupied_days / capacity_days) * 100 if capacity_days > 0 else 0

    return {
        "periodo_inicio": start,
        "periodo_fim": end,
        "taxa_ocupacao_percentual": round(rate, 2),
        "dias_ocupados": occupied_days,
        "capacidade_total_dias": capacity_days
    }
