from app.database import SessionLocal, engine, Base
from app import models

# limpar banco:
# Base.metadata.drop_all(bind=engine)

Base.metadata.create_all(bind=engine)

db = SessionLocal()

def seed():
    print("Iniciando Seed...")

    quartos_data = [
        {"number": 101, "type": models.TypeRoom.SIMPLE, "capacity": 1, "basic_fare": 100.0},
        {"number": 102, "type": models.TypeRoom.DOUBLE, "capacity": 2, "basic_fare": 150.0},
        {"number": 201, "type": models.TypeRoom.LUXURY, "capacity": 3, "basic_fare": 300.0},
        {"number": 202, "type": models.TypeRoom.SIMPLE, "capacity": 1, "basic_fare": 110.0},
    ]

    for q in quartos_data:
        if not db.query(models.Room).filter_by(number=q["number"]).first():
            db.add(models.Room(**q))
            print(f"Quarto {q['number']} criado.")

    hospedes_data = [
        {"name": "Sebastião Soares", "email": "sebastiao@email.com", "phone": "8899999999"},
        {"name": "Ramom Mascena", "email": "ramom@email.com", "phone": "8888888888"},
    ]

    for h in hospedes_data:
        if not db.query(models.Guest).filter_by(email=h["email"]).first():
            db.add(models.Guest(**h))
            print(f"Hóspede {h['name']} criado.")

    db.commit()
    print("Seed concluído com sucesso!")
    db.close()

if __name__ == "__main__":
    seed()