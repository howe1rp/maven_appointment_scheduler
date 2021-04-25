from datetime import datetime, timedelta
from typing import Tuple

from dateutil import parser
from flask import current_app as app
from flask import Blueprint, jsonify, request, Response


appointment_blueprint = Blueprint('appointments', __name__)


class Appointment:
    def __init__(self, start_datetime: datetime):
        self.start_time = start_datetime
        self.end_time = start_datetime + timedelta(minutes=30)

    def format(self) -> dict[str, str]:
        """
        Format the appointment's datetime into a dictionary
        containing the start and end datetimes using
        YYYY-MM-DD HH:MM format.
        :return: a dict containing the formatted start and end appointment times.
        """
        return {
            'start_time': self.start_time.strftime('%Y-%m-%d %H:%M'),
            'end_time': self.end_time.strftime('%Y-%m-%d %H:%M'),
        }

    def dates(self) -> set:
        return {self.start_time.date(), self.end_time.date()}


@appointment_blueprint.route('/<int:user_id>', methods=['GET', 'POST'])
def handle_user_appointments(user_id: int) -> Tuple[Response, int]:
    """
    Get or create an appointment for the specified user.
    NOTE:
        1. A user can only have one appointment on a calendar date.
        2. All appointments must start and end on the hour or half hour.
        3. All appointments are exactly 30 minutes long.
    :param int user_id: the ID of the user
    :return: the JSON response with either the start/end time
    of the new appointment (POST requests) or the start/end time
    for all of the user's appointments.
    """
    if request.method == 'POST':
        request_json = request.get_json()

        appointment_date_str = request_json['appointment']

        try:
            start_datetime = parser.parse(appointment_date_str)
        except parser.ParserError:
            return jsonify({
                'message': 'Appointments must be a valid datetime'
            }), 400

        appointment = Appointment(start_datetime)

        # all appointments must start and end on the hour or half hour
        if start_datetime.minute % 30 != 0:
            return jsonify({
                'message': 'Appointments must start on the hour or half hour'
            }), 400

        if appointments := app.config['APPOINTMENTS'].get(user_id):
            # a user can only have one appointment on a calendar date
            if any(appt.dates() & appointment.dates() for appt in appointments):
                return jsonify({
                    'message': 'User already has an appointment scheduled for this calendar date'
                }), 400

            app.config['APPOINTMENTS'][user_id].append(appointment)
        else:
            app.config['APPOINTMENTS'][user_id] = [appointment]

        return jsonify(appointment.format()), 201

    appointments = app.config['APPOINTMENTS'].get(user_id, [])
    return jsonify({'appointments': [a.format() for a in appointments]})
