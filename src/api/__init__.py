from flask import Flask

from .routes import appointment_blueprint


def create_app():
    app = Flask(__name__)
    app.register_blueprint(appointment_blueprint, url_prefix='/api/appointments')

    app.config['APPOINTMENTS'] = {}

    with app.app_context():
        return app
