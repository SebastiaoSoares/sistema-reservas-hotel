from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app import models, schemas

router = APIRouter()

@router.post("/", response_model=schemas.RoomResponse, status_code=status.HTTP_201_CREATED)
def create_room(room: schemas.RoomCreate, db: Session = Depends(get_db)):
    """
    Cadastra um novo quarto no sistema.
    Verifica se o número já existe para garantir unicidade.
    """

    existing_room = db.query(models.Room).filter(models.Room.number == room.number).first()
    if existing_room:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"O quarto número {room.number} já existe."
        )

    new_room = models.Room(
        number=room.number,
        type=room.type,
        capacity=room.capacity,
        basic_fare=room.basic_fare,
        status=models.StatusRoom.AVAILABLE
    )

    db.add(new_room)
    db.commit()
    db.refresh(new_room)
    return new_room

@router.get("/", response_model=List[schemas.RoomResponse])
def list_rooms(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retorna uma lista de quartos cadastrados.
    Pode ser usado para verificar a persistência e o 'seed'.
    """
    rooms = db.query(models.Room).offset(skip).limit(limit).all()
    return rooms

@router.get("/{room_id}", response_model=schemas.RoomResponse)
def get_room(room_id: int, db: Session = Depends(get_db)):
    """
    Busca os detalhes de um quarto específico.
    """
    room = db.query(models.Room).filter(models.Room.id == room_id).first()
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quarto não encontrado."
        )
    return room

@router.patch("/{room_id}/status", response_model=schemas.RoomResponse)
def update_room_status(room_id: int, new_status: models.StatusRoom, db: Session = Depends(get_db)):
    """
    Altera o status do quarto (ex: colocar em MANUTENCAO ou BLOQUEADO)[cite: 12].
    """
    room = db.query(models.Room).filter(models.Room.id == room_id).first()
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quarto não encontrado."
        )
    
    room.status = new_status
    db.commit()
    db.refresh(room)
    return room

@router.delete("/{room_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_room(room_id: int, db: Session = Depends(get_db)):
    """
    Remove um quarto do sistema.
    """
    room = db.query(models.Room).filter(models.Room.id == room_id).first()
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quarto não encontrado."
        )
    
    db.delete(room)
    db.commit()
    return None