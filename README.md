# 🚕 Ride Hailing System Demo (Uber-like)

## Architecture Diagram

- **Passenger UI**: Requests rides, polls for status, sees driver information
- **Backend (Flask)**: Handles ride, driver, and passenger state, REST API

## How to Run

1. **Install dependencies** (Python 3.10+):
   ```bash
   pip install -r requirements.txt
   ```
2. **Run all components**:
   ```bash
   chmod +x run_all.sh
   ./run_all.sh
   ```
3. **Open in browser:**
   - You can accesss UI at [http://localhost:5050](http://localhost:5050)

## Features

- Request/cancel rides (Passenger)
- Set driver status, accept/cancel rides (Driver)
- Real-time ride status and driver location (polling)
- In-memory state (no DB)
- Minimal, clear Python code

## Tech Stack

- Python 3.10+
- Flask (API backend)
- Requests (API calls)

---

## API Reference

### Authentication

- `POST /login` — Login as passenger or driver
- `POST /signup` — Register as passenger or driver
- `GET /logout` — Logout current user

### Passenger APIs

- `POST /create_ride` — Request a new ride
  - Body: `{ passengerInfo, start, destination }`
  - Response: `{ rideId, ride }`
- `GET /get_ride` — Get latest ride for passenger
- `POST /edit_ride` — Edit ride details
  - Body: `{ rideId, ...fields }`
- `POST /cancel_ride` — Cancel a ride
  - Body: `{ rideId }`
- `GET /ongoing_ride` — Get ongoing ride details
- `GET /pay_for_ride` — Get payment details for current ride
- `POST /complete_payment` — Complete payment for ride
  - Form: `rideId`

### Driver APIs

- `GET /driver_home` — View available ride requests
- `POST /set_driver_status` — Update driver status
  - Body: `{ driverId, status }`
- `POST /accept_ride` — Accept a ride
  - Body: `{ rideId, driverId }`
- `POST /start_ride` — Start an accepted ride
  - Form: `rideId`
- `POST /request_payment` — Request payment from passenger
  - Form: `rideId`
- `POST /end_ride` — Mark ride as completed
  - Form: `rideId`

### Ride APIs

- `GET /get_ride_status` — Get status for a ride
  - Query: `rideId`

### Common APIs

- `GET /ride_accepted` — Get ride accepted status

---

### Notes

- Some endpoints require session authentication (login first).
- For full request/response examples, see the code in `backend/routes/`.

---

## License

MIT License

Copyright (c) [2025] [Shreyas Parab]

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
