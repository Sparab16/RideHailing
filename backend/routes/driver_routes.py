from flask import Blueprint, render_template, redirect, url_for, session, request, jsonify
from datetime import datetime
import random
import state
import json
from helpers import ride_row_to_dict, get_driver, get_ride_by_id

driver_routes = Blueprint('driver_routes', __name__)

@driver_routes.route('/driver_home', methods=['GET', 'POST'])
def driver_home():
    if 'user_id' not in session or session.get('user_type') != 'driver':
        return redirect(url_for('auth_routes.login'))
    driver_id = session.get('user_id')
    driver_name = session.get('user_name', 'Demo Driver')
    ride = None
    with state.get_db() as conn:
        c = conn.cursor()
        c.execute('SELECT * FROM rides WHERE status="REQUESTED" AND driverInfo IS NULL ORDER BY createdAt ASC LIMIT 1')
        row = c.fetchone()
        if row:
            ride = ride_row_to_dict(row)
    return render_template('driver_home.html', username=driver_name, ride=ride)

@driver_routes.route('/set_driver_status', methods=['POST'])
def set_driver_status():
    data = request.json
    driver_id = data['driverId']
    status_str = data['status']
    with state.get_db() as conn:
        c = conn.cursor()
        c.execute('UPDATE drivers SET status=? WHERE id=?', (status_str, driver_id))
        conn.commit()
    return jsonify({'success': True})

@driver_routes.route('/accept_ride', methods=['POST'])
def accept_ride():
    if request.is_json:
        data = request.json
        ride_id = data['rideId']
        driver_id = data['driverId']
    else:
        ride_id = request.form['rideId']
        driver_id = request.form['driverId']
    with state.get_db() as conn:
        c = conn.cursor()
        now = datetime.utcnow().isoformat()
        driverInfo = get_driver(driver_id).__dict__ if driver_id else None
        if not driverInfo:
            return jsonify({'error': 'Driver not found'}), 404
        driverInfo = {
            'id': driverInfo['id'],
            'username': driverInfo['username'],
            'email': driverInfo['email'],
            'car_model': driverInfo.get('car_model', ''),
            'car_number': driverInfo.get('car_number', ''),
            'car_color': driverInfo.get('car_color', ''),
            'eta': random.randint(2, 10),
        }
        c.execute('UPDATE rides SET driverInfo=?, status=?, startTime=? WHERE rideId=?',
                  (json.dumps(driverInfo), 'ACCEPTED', now, ride_id))
        conn.commit()
    ride = get_ride_by_id(ride_id)
    if request.is_json:
        return jsonify({'ride': ride})
    else:
        return render_template('driver_ride_accepted.html', ride=ride)

@driver_routes.route('/start_ride', methods=['POST'])
def start_ride():
    if 'user_id' not in session or session.get('user_type') != 'driver':
        return redirect(url_for('auth_routes.login'))
    ride_id = request.form['rideId']
    with state.get_db() as conn:
        c = conn.cursor()
        # Only allow if current status is ACCEPTED
        c.execute('SELECT status FROM rides WHERE rideId=?', (ride_id,))
        row = c.fetchone()
        if not row or row[0] != 'ACCEPTED':
            return redirect(url_for('driver_routes.driver_home'))
        c.execute('UPDATE rides SET status=? WHERE rideId=?', ('ONGOING', ride_id))
        conn.commit()
    # Fetch updated ride and render ongoing ride UI
    ride = get_ride_by_id(ride_id)
    return render_template('ongoing_ride_driver.html', ride=ride, user_type='driver')

@driver_routes.route('/request_payment', methods=['POST'])
def request_payment():
    if 'user_id' not in session or session.get('user_type') != 'driver':
        return redirect(url_for('auth_routes.login'))
    
    ride_id = request.form['rideId']
    with state.get_db() as conn:
        c = conn.cursor()
        # Only allow if current status is ONGOING
        c.execute('SELECT status FROM rides WHERE rideId=?', (ride_id,))
        row = c.fetchone()
        if not row or row[0] != 'ONGOING':
            return redirect(url_for('driver_home'))
        c.execute('UPDATE rides SET status=? WHERE rideId=?', ('PAYMENT_REQUESTED', ride_id))
        conn.commit()
        
    return jsonify({'status': "ok"})

@driver_routes.route('/end_ride', methods=['POST'])
def end_ride():
    if 'user_id' not in session or session.get('user_type') != 'driver':
        return redirect(url_for('auth_routes.login'))
    ride_id = request.form['rideId']
    with state.get_db() as conn:
        c = conn.cursor()
        # Only allow if current status is PAYMENT_DONE
        c.execute('SELECT status FROM rides WHERE rideId=?', (ride_id,))
        row = c.fetchone()
        if not row or row[0] != 'PAYMENT_DONE':
            return redirect(url_for('driver_routes.driver_home'))
        c.execute('UPDATE rides SET status=? WHERE rideId=?', ('COMPLETED', ride_id))
        conn.commit()
    return jsonify({'status': "ok"})
