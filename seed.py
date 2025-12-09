from app.database import SessionLocal, engine, Base
from app import models
from datetime import date, timedelta

# limpar banco:
Base.metadata.drop_all(bind=engine)

Base.metadata.create_all(bind=engine)

db = SessionLocal()

def seed():
    print("Iniciando Seed...")

    quartos_data = [
        {"number": 101, "type": models.TypeRoom.SIMPLE, "capacity": 1, "basic_fare": 100.0, "status": models.StatusRoom.AVAILABLE},
        {"number": 102, "type": models.TypeRoom.DOUBLE, "capacity": 2, "basic_fare": 150.0, "status": models.StatusRoom.AVAILABLE},
        {"number": 201, "type": models.TypeRoom.LUXURY, "capacity": 3, "basic_fare": 300.0, "status": models.StatusRoom.AVAILABLE},
        {"number": 202, "type": models.TypeRoom.SIMPLE, "capacity": 1, "basic_fare": 110.0, "status": models.StatusRoom.AVAILABLE},

        # teste da manutenção de um quarto
        {"number": 301, "type": models.TypeRoom.DOUBLE, "capacity": 2, "basic_fare": 140.0, "status": models.StatusRoom.MAINTENANCE},
    ]

    rooms_objs = {} 

    for q in quartos_data:
        room = models.Room(**q)
        db.add(room)
        db.commit()
        db.refresh(room)
        rooms_objs[room.number] = room
        print(f"Quarto {room.number} criado (Status: {room.status}).")

    hospedes_data = [
        {"name": "Sebastião Soares", "email": "sebastiao@email.com", "phone": "8899999999"},
        {"name": "Ramom Mascena", "email": "ramom@email.com", "phone": "8888888888"},
        {"name": "Jayr", "email": "jayr@email.com", "phone": "1199999999"},
    ]

    guests_objs = {}

    for h in hospedes_data:
        guest = models.Guest(**h)
        db.add(guest)
        db.commit()
        db.refresh(guest)
        guests_objs[guest.name] = guest
        print(f"Hóspede {guest.name} criado.")
    
    # exemplo de reserva confirmada - ramom no quarto 201
    res_futura = models.Reservation(
        guest_id=guests_objs["Ramom Mascena"].id,
        room_id=rooms_objs[201].id,
        check_in=date.today() + timedelta(days=7),
        check_out=date.today() + timedelta(days=10),
        n_guests=2,
        status=models.StatusReservation.CONFIRMED
    )
    db.add(res_futura)
    print("Reserva CONFIRMADA criada para Ramom (Quarto 201).")

    # reserva em andamento - sebastião está no quarto 101
    res_ativa = models.Reservation(
        guest_id=guests_objs["Sebastião Soares"].id,
        room_id=rooms_objs[101].id,
        check_in=date.today() - timedelta(days=1),
        check_out=date.today() + timedelta(days=1),
        n_guests=1,
        status=models.StatusReservation.CHECKIN
    )
    
    rooms_objs[101].status = models.StatusRoom.OCCUPIED
    
    db.add(res_ativa)
    db.commit()
    db.refresh(res_ativa)
    print("Reserva em CHECKIN criada para Sebastião (Quarto 101 - Ocupado).")
    
    # sebastião consumiu coisas no quarto
    adicionais = [
        {"description": "Coca-Cola Lata", "value": 6.50, "reservation_id": res_ativa.id},
        {"description": "Batata Pringles", "value": 15.00, "reservation_id": res_ativa.id},
        {"description": "Lavanderia (Camisa)", "value": 25.00, "reservation_id": res_ativa.id},
    ]

    for add in adicionais:
        db.add(models.Additional(**add))
    
    print(f"Adicionados {len(adicionais)} itens de consumo para a reserva do Sebastião.")

    db.commit()
    print("Seed concluído com sucesso!")
    db.close()

if __name__ == "__main__":
    seed()