# models.py

from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from datetime import datetime

@dataclass
class VehicleInfo:
    licensePlate: str
    description: str

@dataclass
class PassengerInfo:
    id: str
    email: str
    username: str

@dataclass
class DriverInfo:
    id: str
    email: str
    username: str
    car_model: Optional[str] = None
    car_number: Optional[str] = None
    car_color: Optional[str] = None

@dataclass
class Ride:
    rideId: str
    passengerInfo: PassengerInfo
    driverInfo: Optional[DriverInfo] = None
    status: str = "REQUESTED"  # REQUESTED, ACCEPTED, ONGOING, COMPLETED, CANCELLED
    start: str = ""
    destination: str = ""
    estimatedPrice: float = 0.0
    timeToDestination: int = 0
    startTime: Optional[datetime] = None
    createdAt: datetime = field(default_factory=datetime.utcnow)
    driverLocation: Optional[Dict[str, Any]] = field(default_factory=dict)
