from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app import models, schemas

router = APIRouter()

@router.post("/", response_model=schemas.GuestResponse, status_code=status.HTTP_201_CREATED)
def create_guest(guest: schemas.GuestCreate, db: Session = Depends(get_db)):

    if db.query(models.Guest).filter(models.Guest.email == guest.email).first():
        raise HTTPException(status_code=400, detail="E-mail já cadastrado.")

    new_guest = models.Guest(**guest.dict())
    db.add(new_guest)
    db.commit()
    db.refresh(new_guest)
    return new_guest

@router.get("/", response_model=List[schemas.GuestResponse])
def list_guests(db: Session = Depends(get_db)):
    return db.query(models.Guest).all()

@router.get("/{guest_id}", response_model=schemas.GuestResponse)
def get_guest(guest_id: int, db: Session = Depends(get_db)):
    guest = db.query(models.Guest).filter(models.Guest.id == guest_id).first()
    if not guest:
        raise HTTPException(status_code=404, detail="Hóspede não encontrado.")
    return guest