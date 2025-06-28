# app.py
from flask import Flask
from flask_cors import CORS # type: ignore

# Import blueprints
from routes.passenger_routes import passenger_routes
from routes.driver_routes import driver_routes
from routes.ride_routes import ride_routes
from routes.auth_routes import auth_routes
from routes.common_routes import common_routes

import os

app = Flask(__name__)
CORS(app)
app.secret_key = os.environ.get("SECRET_KEY", 'fallback_secret_key')

# Register blueprints
app.register_blueprint(passenger_routes)
app.register_blueprint(driver_routes)
app.register_blueprint(ride_routes)
app.register_blueprint(auth_routes)
app.register_blueprint(common_routes)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
