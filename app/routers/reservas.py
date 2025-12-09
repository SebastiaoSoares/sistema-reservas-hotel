from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas, utils 
from typing import List

router = APIRouter()

@router.post("/", response_model=schemas.ReservationResponse, status_code=status.HTTP_201_CREATED)
def create_reservation(res: schemas.ReservationCreate, db: Session = Depends(get_db)):

    room = db.query(models.Room).filter(models.Room.id == res.room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Quarto não encontrado")

    if res.n_guests > room.capacity:
        raise HTTPException(status_code=400, detail="Capacidade do quarto excedida")
    
    if res.check_in >= res.check_out:
        raise HTTPException(status_code=400, detail="Data de check-in deve ser anterior ao check-out")

    if not utils.is_room_available(db, res.room_id, res.check_in, res.check_out):
        raise HTTPException(status_code=400, detail="Quarto indisponível para este período.")

    new_res = models.Reservation(
        **res.dict(),
        status=models.StatusReservation.CONFIRMED
    )
    
    db.add(new_res)
    db.commit()
    db.refresh(new_res)
    return new_res

@router.post("/{res_id}/checkin")
def check_in(res_id: int, db: Session = Depends(get_db)):
    res = db.query(models.Reservation).filter(models.Reservation.id == res_id).first()
    if not res:
        raise HTTPException(status_code=404, detail="Reserva não encontrada")

    if res.status != models.StatusReservation.CONFIRMED:
        raise HTTPException(status_code=400, detail="Apenas reservas CONFIRMADAS podem fazer check-in")
    
    res.status = models.StatusReservation.CHECKIN
    res.room.status = models.StatusRoom.OCCUPIED
    
    db.commit()
    return {"message": "Check-in realizado com sucesso", "status": "CHECKIN"}

@router.post("/{res_id}/checkout")
def check_out(res_id: int, db: Session = Depends(get_db)):
    res = db.query(models.Reservation).filter(models.Reservation.id == res_id).first()
    
    if not res or res.status != models.StatusReservation.CHECKIN:
        raise HTTPException(status_code=400, detail="Reserva deve estar em CHECKIN para realizar checkout")

    valor_diarias = utils.calculate_total_price(
        room_price=res.room.basic_fare,
        check_in=res.check_in,
        check_out=res.check_out
    )
    
    valor_adicionais = sum([add.value for add in res.additionals])
    valor_total = valor_diarias + valor_adicionais
    
    res.status = models.StatusReservation.CHECKOUT
    res.room.status = models.StatusRoom.AVAILABLE
    
    db.commit()
    
    return {
        "message": "Check-out realizado",
        "resumo": {
            "valor_diarias": valor_diarias,
            "valor_adicionais": valor_adicionais,
            "total_final": valor_total
        }
    }

@router.post("/{res_id}/cancel")
def cancel_reservation(res_id: int, db: Session = Depends(get_db)):
    res = db.query(models.Reservation).filter(models.Reservation.id == res_id).first()
    if not res:
        raise HTTPException(status_code=404, detail="Reserva não encontrada")
    
    if res.status in [models.StatusReservation.CHECKIN, models.StatusReservation.CHECKOUT]:
         raise HTTPException(status_code=400, detail="Não é possível cancelar reservas em andamento ou finalizadas")

    res.status = models.StatusReservation.CANCELED

    res.room.status = models.StatusRoom.AVAILABLE 
    
    db.commit()
    return {"message": "Reserva cancelada com sucesso"}

@router.get("/{res_id}/additionals", response_model=List[schemas.AdditionalResponse])
def get_additionals(res_id: int, db: Session = Depends(get_db)):

    if not db.query(models.Reservation).filter(models.Reservation.id == res_id).first():
        raise HTTPException(status_code=404, detail="Reserva não encontrada")


    return db.query(models.Additional).filter(models.Additional.reservation_id == res_id).all()

@router.post("/{res_id}/adicionais", response_model=schemas.AdditionalResponse)
def add_additional(res_id: int, add: schemas.AdditionalCreate, db: Session = Depends(get_db)):

    res = db.query(models.Reservation).filter(models.Reservation.id == res_id).first()
    if not res:
        raise HTTPException(status_code=404, detail="Reserva não encontrada")

    if res.status in [models.StatusReservation.CHECKOUT, models.StatusReservation.CANCELED]:
        raise HTTPException(status_code=400, detail="Não é possível lançar adicionais em reservas fechadas.")

    new_additional = models.Additional(
        description=add.description,
        value=add.value,
        reservation_id=res_id
    )
    
    db.add(new_additional)
    db.commit()
    db.refresh(new_additional)
    
    return new_additional
