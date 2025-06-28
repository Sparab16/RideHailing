from flask import Blueprint, redirect, url_for, session, render_template, send_from_directory, request
import state
from helpers import get_ride_by_id

common_routes = Blueprint('common_routes', __name__)

@common_routes.route('/')
def home():
    if 'user_id' in session:
        user_type = session.get('user_type')
        if user_type == 'passenger':
            return redirect(url_for('passenger_routes.passenger_home'))
        elif user_type == 'driver':
            return redirect(url_for('driver_routes.driver_home'))
    return redirect(url_for('auth_routes.login'))

@common_routes.route('/ride_accepted')
def ride_accepted():
    ride_id = request.args.get('rideId')
    ride = get_ride_by_id(ride_id) if ride_id else None
    user_type = session.get('user_type')
    if user_type == 'driver':
        return render_template('driver_ride_accepted.html', ride=ride)
    else:
        return render_template('ride_accepted.html', ride=ride)

@common_routes.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

@common_routes.route('/get_ride_status')
def get_ride_status():
    # Accept both 'rideId' and 'ride_id' for robustness
    ride_id = request.args.get('rideId') or request.args.get('ride_id')
    if not ride_id:
        return {'status': 'UNKNOWN'}
    with state.get_db() as conn:
        c = conn.cursor()
        c.execute('SELECT status FROM rides WHERE rideId=?', (ride_id,))
        row = c.fetchone()
        print(row)
        if row:
            return {'status': row[0]}
        else:
            return {'status': 'UNKNOWN'}

@common_routes.route('/end_ride', methods=['POST'])
def end_ride():
    ride_id = request.form.get('rideId') or request.json.get('rideId')
    if not ride_id:
        return {'success': False, 'error': 'Missing rideId'}, 400
    with state.get_db() as conn:
        c = conn.cursor()
        c.execute('UPDATE rides SET status=? WHERE rideId=?', ('COMPLETED', ride_id))
        conn.commit()
    return {'success': True, 'status': 'COMPLETED'}
