from datetime import date, timedelta
from sqlalchemy.orm import Session
from app.models import Reservation, Room, StatusReservation
from app.settings import SETTINGS

def calculate_total_price(room_price: float, check_in: date, check_out: date) -> float:
    total = 0.0
    current_date = check_in
    while current_date < check_out:
        daily_rate = room_price
        
        if current_date.weekday() >= 5:
            daily_rate *= SETTINGS["WEEKEND_MULTIPLIER"]
        
        if current_date.month in SETTINGS["HIGH_SEASON_MONTHS"]:
            daily_rate *= SETTINGS["SEASON_MULTIPLIER"]
            
        total += daily_rate
        current_date += timedelta(days=1)
    
    return round(total, 2)

def is_room_available(db: Session, room_id: int, check_in: date, check_out: date) -> bool:
    overlapping = db.query(Reservation).filter(
        Reservation.room_id == room_id,
        Reservation.status.in_([StatusReservation.CONFIRMED, StatusReservation.CHECKIN]),
        Reservation.check_in < check_out,
        Reservation.check_out > check_in
    ).first()
    
    return overlapping is None
