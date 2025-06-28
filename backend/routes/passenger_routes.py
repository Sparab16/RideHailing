from flask import Blueprint, render_template, redirect, url_for, session, request, jsonify
import uuid
from datetime import datetime
import random
import state
from helpers import ride_row_to_dict, get_passenger

passenger_routes = Blueprint('passenger_routes', __name__)

@passenger_routes.route('/passenger_home', methods=['GET', 'POST'])
def passenger_home():
    if 'user_id' not in session or session.get('user_type') != 'passenger':
        return redirect(url_for('auth_routes.login'))
    if request.method == 'POST':
        start = request.form['start']
        destination = request.form['destination']
        passenger_id = session.get('user_id')
        passenger_name = session.get('user_name', 'Demo Passenger')
        with state.get_db() as conn:
            c = conn.cursor()
            ride_id = str(uuid.uuid4())
            now = datetime.utcnow().isoformat()
            c.execute('''INSERT INTO rides (rideId, passengerId, driverId, status, start, destination, estimatedPrice, timeToDestination, startTime, createdAt)
                         VALUES (?, ?, NULL, ?, ?, ?, ?, ?, NULL, ?)''',
                      (ride_id, passenger_id, 'REQUESTED', start, destination,
                       random.randint(10, 500), random.randint(10, 60), now))
            conn.commit()
        return redirect(url_for('passenger_routes.waiting_for_driver'))
    return render_template('passenger_home.html', username=session.get('user_name'))

@passenger_routes.route('/waiting_for_driver')
def waiting_for_driver():
    return render_template('waiting_for_driver.html')

@passenger_routes.route('/cancel_ride', methods=['POST'])
def cancel_ride():
    if request.is_json:
        data = request.json
        ride_id = data['rideId']
    else:
        ride_id = request.form['rideId']
    with state.get_db() as conn:
        c = conn.cursor()
        c.execute('UPDATE rides SET status=? WHERE rideId=?', ('CANCELLED', ride_id))
        conn.commit()
    return render_template("/passenger_home.html", message="Ride cancelled successfully", username=session.get('user_name'))

@passenger_routes.route('/ongoing_ride')
def ongoing_ride():
    if 'user_id' not in session or session.get('user_type') != 'passenger':
        return redirect(url_for('auth_routes.login'))
    passenger_id = session.get('user_id')
    with state.get_db() as conn:
        c = conn.cursor()
        c.execute('SELECT * FROM rides WHERE passengerId=? AND status=? ORDER BY createdAt DESC LIMIT 1', (passenger_id, 'ONGOING'))
        row = c.fetchone()
        if not row:
            return redirect(url_for('passenger_routes.passenger_home'))
        ride = ride_row_to_dict(row)
    return render_template('ongoing_ride_passenger.html', ride=ride, user_type='passenger')

@passenger_routes.route('/pay_for_ride', methods=['GET'])
def pay_for_ride():
    if 'user_id' not in session or session.get('user_type') != 'passenger':
        return redirect(url_for('auth_routes.login'))
    passenger_id = session.get('user_id')
    with state.get_db() as conn:
        c = conn.cursor()
        c.execute('SELECT * FROM rides WHERE passengerId=? AND status=? ORDER BY createdAt DESC LIMIT 1', (passenger_id, 'PAYMENT_PENDING'))
        row = c.fetchone()
        if not row:
            return redirect(url_for('passenger_routes.passenger_home'))
        ride = ride_row_to_dict(row)
    return render_template('pay_for_ride.html', ride=ride)

@passenger_routes.route('/complete_payment', methods=['POST'])
def complete_payment():
    if 'user_id' not in session or session.get('user_type') != 'passenger':
        return redirect(url_for('auth_routes.login'))
    
    ride_id = request.form['rideId']
    print(ride_id)
    with state.get_db() as conn:
        c = conn.cursor()
        c.execute('SELECT status FROM rides WHERE rideId=?', (ride_id,))
        row = c.fetchone()
        if not row or row[0] != 'PAYMENT_REQUESTED':
            return redirect(url_for('passenger_routes.passenger_home'))
        c.execute('UPDATE rides SET status=? WHERE rideId=?', ('PAYMENT_DONE', ride_id))
        conn.commit()
    return render_template('passenger_home.html', message='Payment successful! Ride completed.', username=session.get('user_name'))
