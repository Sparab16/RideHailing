from flask import Blueprint, request, jsonify, session, redirect, url_for
from datetime import datetime
import state
import json
from helpers import ride_row_to_dict, get_ride_by_id

ride_routes = Blueprint('ride_routes', __name__)

@ride_routes.route('/create_ride', methods=['POST'])
def create_ride():
    if request.is_json:
        data = request.json
        passenger = data['passengerInfo']
        passenger_id = passenger['id']
        start = data['start'][:5]
        destination = data['destination'][:5]
    else:
        if 'user_id' not in session or session.get('user_type') != 'passenger':
            return redirect(url_for('auth_routes.login'))
        passenger_id = session.get('user_id')
        start = request.form['start'][:7]
        destination = request.form['destination'][:7]
    with state.get_db() as conn:
        c = conn.cursor()
        import uuid
        from datetime import datetime
        import random
        ride_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        c.execute('''INSERT INTO rides (rideId, passengerId, driverInfo, status, start, destination, estimatedPrice, timeToDestination, startTime, createdAt)
                     VALUES (?, ?, NULL, ?, ?, ?, ?, ?, NULL, ?)''',
                  (ride_id, passenger_id, 'REQUESTED', start, destination,
                   random.randint(0, 500), random.randint(0, 60), now))
        conn.commit()
    if request.is_json:
        return jsonify({'rideId': ride_id, 'ride': get_ride_by_id(ride_id)})
    else:
        return redirect(url_for('passenger_routes.waiting_for_driver'))

@ride_routes.route('/get_ride', methods=['GET'])
def get_ride():
    user_id = session.get('user_id')
    user_type = session.get('user_type')
    with state.get_db() as conn:
        c = conn.cursor()
        if user_type == 'passenger':
            c.execute('SELECT * FROM rides WHERE passengerId=? ORDER BY createdAt DESC LIMIT 1', (user_id,))
        elif user_type == 'driver':
            c.execute('SELECT * FROM rides WHERE status="REQUESTED" AND driverInfo IS NULL ORDER BY createdAt ASC LIMIT 1')
        row = c.fetchone()
        if row:
            return jsonify({'ride': ride_row_to_dict(row)})
    return jsonify({'ride': None})

@ride_routes.route('/edit_ride', methods=['POST'])
def edit_ride():
    data = request.json
    ride_id = data['rideId']
    fields = [k for k in data if k != 'rideId']
    if not fields:
        return jsonify({'error': 'No fields to update'}), 400
    with state.get_db() as conn:
        c = conn.cursor()
        for k in fields:
            c.execute(f'UPDATE rides SET {k}=? WHERE rideId=?', (data[k], ride_id))
        conn.commit()
    return jsonify({'ride': get_ride_by_id(ride_id)})

@ride_routes.route('/push_location', methods=['POST'])
def push_location():
    data = request.json
    ride_id = data['rideId']
    location = data['location']
    now = datetime.utcnow().isoformat()
    with state.get_db() as conn:
        c = conn.cursor()
        c.execute('INSERT INTO ride_locations (rideId, lat, lon, timestamp) VALUES (?, ?, ?, ?)',
                  (ride_id, location['lat'], location['lon'], now))
        conn.commit()
    return jsonify({'success': True})

@ride_routes.route('/stream_location', methods=['GET'])
def stream_location():
    user_id = request.args.get('userId')
    with state.get_db() as conn:
        c = conn.cursor()
        c.execute('SELECT rideId FROM rides WHERE passengerId=? OR driverId=? ORDER BY createdAt DESC LIMIT 1', (user_id, user_id))
        row = c.fetchone()
        if not row:
            return jsonify({'locations': []})
        ride_id = row[0]
        c.execute('SELECT lat, lon, timestamp FROM ride_locations WHERE rideId=? ORDER BY timestamp', (ride_id,))
        locs = [{'lat': lat, 'lon': lon, 'timestamp': ts} for lat, lon, ts in c.fetchall()]
        return jsonify({'locations': locs})
