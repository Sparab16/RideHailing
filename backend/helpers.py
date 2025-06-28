import json
from models import PassengerInfo, DriverInfo
import state
import bcrypt

def get_passenger(passenger_id):
    with state.get_db() as conn:
        c = conn.cursor()
        c.execute('SELECT id, username, email FROM passengers WHERE id=?', (passenger_id,))
        row = c.fetchone()
        if row:
            return PassengerInfo(id=row[0], username=row[1], email=row[2])
        return None

def get_driver(driver_id):
    with state.get_db() as conn:
        c = conn.cursor()
        c.execute('SELECT id, username, email, car_model, car_number, car_color  FROM drivers WHERE id=?', (driver_id,))
        row = c.fetchone()
        if row:
            return DriverInfo(id=row[0], username=row[1], email=row[2], 
                              car_model=row[3], car_number=row[4], car_color=row[5])
        return None

def ride_row_to_dict(row):
    return {
        'rideId': row[0],
        'passengerId': row[1],
        'driverInfo': json.loads(row[2]) if row[2] else None,
        'status': row[3],
        'start': row[4],
        'destination': row[5],
        'estimatedPrice': row[6],
        'timeToDestination': row[7],
        'startTime': row[8],
        'createdAt': row[9],
    }

def get_ride_by_id(ride_id):
    with state.get_db() as conn:
        c = conn.cursor()
        c.execute('SELECT * FROM rides WHERE rideId=?', (ride_id,))
        row = c.fetchone()
        if not row:
            return None
        ride = ride_row_to_dict(row)
        ride['passengerInfo'] = get_passenger(ride['passengerId']).__dict__ if ride['passengerId'] else None
        ride['driverInfo'] = get_driver(ride['driverInfo']['id']).__dict__ if ride['driverInfo'] else None
        return ride

def hash_password(password: str) -> bytes:
    """Hash a password for storing in the database."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def check_password(password: str, hashed: bytes) -> bool:
    """Verify a stored password against one provided by user."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed)
