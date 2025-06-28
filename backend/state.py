# state.py

import sqlite3
from contextlib import contextmanager

DB_PATH = 'rides.db'  # Use ':memory:' for in-memory only

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS passengers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT,
            password TEXT,
            username TEXT
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS drivers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT,
            password TEXT,
            username TEXT,
            car_model TEXT,
            car_number TEXT,
            car_color TEXT
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS rides (
            rideId TEXT PRIMARY KEY,
            passengerId TEXT,
            driverInfo TEXT,
            status TEXT,
            start TEXT,
            destination TEXT,
            estimatedPrice REAL,
            timeToDestination INTEGER,
            startTime TEXT,
            createdAt TEXT
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS ride_locations (
            rideId TEXT,
            lat REAL,
            lon REAL,
            timestamp TEXT
        )''')

@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
    finally:
        conn.close()

init_db()
