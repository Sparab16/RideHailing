from flask import Blueprint, render_template, redirect, url_for, session, request
import sqlite3
import state
from helpers import check_password, hash_password

auth_routes = Blueprint('auth_routes', __name__)

@auth_routes.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        user_type = request.form['user_type']
        password = request.form['password']
        with state.get_db() as conn:
            c = conn.cursor()
            if user_type == 'passenger':
                c.execute('SELECT id, password FROM passengers WHERE email=?', (email,))
            elif user_type == 'driver':
                c.execute('SELECT id, password FROM drivers WHERE email=?', (email,))
            user = c.fetchone()
            if user and check_password(password, user[1]):
                session['user_id'] = user[0]
                session['user_type'] = user_type
                return redirect(url_for('common_routes.home'))
            else:
                return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

@auth_routes.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        user_type = request.form['user_type']
        hashed_password = hash_password(password)
        with state.get_db() as conn:
            c = conn.cursor()
            try:
                if user_type == 'passenger':
                    c.execute('INSERT INTO passengers (email, username, password) VALUES (?, ?, ?)', (email, username, hashed_password))
                elif user_type == 'driver':
                    car_model = request.form.get('car_model', '')
                    car_number = request.form.get('car_number', '')
                    car_color = request.form.get('car_color', '')
                    c.execute('INSERT INTO drivers (email, username, password, car_model, car_number, car_color) VALUES (?, ?, ?, ?, ?, ?)', 
                              (email, username, hashed_password, car_model, car_number, car_color))
                conn.commit()
            except sqlite3.IntegrityError:
                return render_template('signup.html', error='Email or username already exists')
            session['user_id'] = c.lastrowid
            session['user_name'] = username
            session['user_type'] = user_type
            return redirect(url_for('common_routes.home'))
    return render_template('signup.html')

@auth_routes.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth_routes.login'))
