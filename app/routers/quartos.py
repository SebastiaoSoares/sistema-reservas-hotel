from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app import models, schemas

router = APIRouter()

@router.post("/", response_model=schemas.RoomResponse, status_code=status.HTTP_201_CREATED)
def create_room(room: schemas.RoomCreate, db: Session = Depends(get_db)):

    existing_room = db.query(models.Room).filter(models.Room.number == room.number).first()
    if existing_room:
        raise HTTPException(status_code=400, detail=f"O quarto {room.number} já existe.")

    new_room = models.Room(**room.dict(), status=models.StatusRoom.AVAILABLE)
    db.add(new_room)
    db.commit()
    db.refresh(new_room)
    return new_room

@router.get("/", response_model=List[schemas.RoomResponse])
def list_rooms(db: Session = Depends(get_db)):
    return db.query(models.Room).all()

@router.get("/{room_id}", response_model=schemas.RoomResponse)
def get_room(room_id: int, db: Session = Depends(get_db)):
    room = db.query(models.Room).filter(models.Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Quarto não encontrado.")
    return room

@router.patch("/{room_id}/status")
def update_room_status(room_id: int, new_status: models.StatusRoom, db: Session = Depends(get_db)):
    room = db.query(models.Room).filter(models.Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Quarto não encontrado.")
    
    room.status = new_status
    db.commit()
    return {"message": f"Status atualizado para {new_status.value}"}