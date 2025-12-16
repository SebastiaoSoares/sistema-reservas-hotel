from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas, settings, utils
from typing import List
from datetime import date

router = APIRouter()

# criar reserva
@router.post("/", response_model=schemas.ReservationResponse, status_code=status.HTTP_201_CREATED)
def create_reservation(res: schemas.ReservationCreate, db: Session = Depends(get_db)):
    # busca quarto
    room = db.query(models.Room).filter(models.Room.id == res.room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Quarto não encontrado")

    # valida capacidade
    if res.n_guests > room.capacity:
        raise HTTPException(status_code=400, detail="Capacidade do quarto excedida")
    
    # valida datas
    if res.check_in >= res.check_out:
        raise HTTPException(status_code=400, detail="Data de check-in deve ser anterior ao check-out")

    # valida disponibilidade
    if not utils.is_room_available(db, res.room_id, res.check_in, res.check_out):
        raise HTTPException(status_code=400, detail="Quarto indisponível para este período.")

    try:
        # cria
        new_res = models.Reservation(
            **res.dict(),
            status=models.StatusReservation.CONFIRMED
        )
        db.add(new_res)
        db.commit()
        db.refresh(new_res)
        return new_res
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# checkin
@router.post("/{res_id}/checkin")
def check_in(res_id: int, db: Session = Depends(get_db)):
    # busca
    res = db.query(models.Reservation).filter(models.Reservation.id == res_id).first()
    if not res:
        raise HTTPException(status_code=404, detail="Reserva não encontrada")

    # valida status
    if res.status != models.StatusReservation.CONFIRMED:
        raise HTTPException(status_code=400, detail="Apenas reservas CONFIRMADAS podem fazer check-in")
    
    # valida data
    if date.today() < res.check_in:
         raise HTTPException(status_code=400, detail="Check-in não permitido antes da data agendada.")

    # atualiza
    res.status = models.StatusReservation.CHECKIN
    res.room.status = models.StatusRoom.OCCUPIED
    
    db.commit()
    return {"message": "Check-in realizado com sucesso", "status": "CHECKIN"}

# registrar pagamento
@router.post("/{res_id}/pagamentos", status_code=status.HTTP_201_CREATED)
def registrar_pagamento(res_id: int, pag: schemas.PaymentCreate, db: Session = Depends(get_db)):
    # busca
    res = db.query(models.Reservation).filter(models.Reservation.id == res_id).first()
    if not res:
        raise HTTPException(status_code=404, detail="Reserva não encontrada")

    # registra
    novo_pagamento = models.Payment(
        method=pag.method,
        value=pag.value,
        reservation_id=res_id
    )
    db.add(novo_pagamento)
    db.commit()
    return {"message": "Pagamento registrado", "valor": pag.value}

# checkout
@router.post("/{res_id}/checkout")
def check_out(res_id: int, db: Session = Depends(get_db)):
    # busca
    res = db.query(models.Reservation).filter(models.Reservation.id == res_id).first()
    
    # valida status
    if not res or res.status != models.StatusReservation.CHECKIN:
        raise HTTPException(status_code=400, detail="Reserva deve estar em CHECKIN para realizar checkout")

    # calculo total
    valor_diarias = utils.calculate_total_price(
        room_price=res.room.basic_fare,
        check_in=res.check_in,
        check_out=res.check_out
    )
    valor_adicionais = sum([add.value for add in res.additionals])
    total_devido = valor_diarias + valor_adicionais
    total_pago = sum([p.value for p in res.payments])

    # verifica divida
    if total_pago < total_devido:
        falta = total_devido - total_pago
        raise HTTPException(
            status_code=400, 
            detail=f"Check-out bloqueado. Pendente: R$ {falta:.2f}. (Pago: {total_pago}, Total: {total_devido})"
        )

    # atualiza
    res.status = models.StatusReservation.CHECKOUT
    res.room.status = models.StatusRoom.AVAILABLE
    
    db.commit()
    
    return {
        "message": "Check-out realizado",
        "financeiro": {
            "total_servicos": total_devido,
            "total_pago": total_pago,
            "troco": total_pago - total_devido
        }
    }

# cancelamento
@router.post("/{res_id}/cancel")
def cancel_reservation(res_id: int, db: Session = Depends(get_db)):
    # busca
    res = db.query(models.Reservation).filter(models.Reservation.id == res_id).first()
    if not res:
        raise HTTPException(status_code=404, detail="Reserva não encontrada")
    
    # valida status
    if res.status in [models.StatusReservation.CHECKIN, models.StatusReservation.CHECKOUT]:
         raise HTTPException(status_code=400, detail="Não é possível cancelar reservas em andamento.")

    mensagem = "Reserva cancelada com sucesso"
    
    # aplica multa
    if date.today() >= res.check_in:
        total_estimado = utils.calculate_total_price(res.room.basic_fare, res.check_in, res.check_out)
        valor_multa = total_estimado * settings.SETTINGS["CANCELLATION_FEE_PERCENT"]
        
        multa = models.Additional(
            description="Multa de Cancelamento Tardio",
            value=valor_multa,
            reservation_id=res.id
        )
        db.add(multa)
        mensagem = f"Reserva cancelada com MULTA de R$ {valor_multa:.2f} aplicada."

    # cancela
    res.status = models.StatusReservation.CANCELED
    res.room.status = models.StatusRoom.AVAILABLE 
    
    db.commit()
    return {"message": mensagem}

# rotina no-show
@router.post("/rotinas/processar-no-show")
def process_no_shows(db: Session = Depends(get_db)):
    # busca atrasados
    reservas_atrasadas = db.query(models.Reservation).filter(
        models.Reservation.status == models.StatusReservation.CONFIRMED,
        models.Reservation.check_in < date.today() 
    ).all()
    
    # atualiza em lote
    count = 0
    for r in reservas_atrasadas:
        r.status = models.StatusReservation.NO_SHOW
        r.room.status = models.StatusRoom.AVAILABLE
        count += 1
    
    db.commit()
    return {"message": f"{count} reservas marcadas como NO_SHOW."}

# listar adicionais
@router.get("/{res_id}/additionals", response_model=List[schemas.AdditionalResponse])
def get_additionals(res_id: int, db: Session = Depends(get_db)):
    # busca
    if not db.query(models.Reservation).filter(models.Reservation.id == res_id).first():
        raise HTTPException(status_code=404, detail="Reserva não encontrada")
    return db.query(models.Additional).filter(models.Additional.reservation_id == res_id).all()

# criar adicional
@router.post("/{res_id}/adicionais", response_model=schemas.AdditionalResponse)
def add_additional(res_id: int, add: schemas.AdditionalCreate, db: Session = Depends(get_db)):
    # busca
    res = db.query(models.Reservation).filter(models.Reservation.id == res_id).first()
    if not res:
        raise HTTPException(status_code=404, detail="Reserva não encontrada")

    # valida status
    if res.status in [models.StatusReservation.CHECKOUT, models.StatusReservation.CANCELED]:
        raise HTTPException(status_code=400, detail="Não permitido em reservas fechadas.")

    # cria
    new_additional = models.Additional(
        description=add.description,
        value=add.value,
        reservation_id=res_id
    )
    db.add(new_additional)
    db.commit()
    db.refresh(new_additional)
    return new_additional