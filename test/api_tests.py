import pytest

from datetime import datetime

from src.api import create_app
from src.api.routes import Appointment


@pytest.fixture
def client():
    app = create_app()
    app.testing = True

    with app.test_client() as client:
        yield client


def test_get_user_appointments(client):
    """
    Test that the user's appointments are returned
    with a GET request.
    """
    appt_datetime = datetime(2021, 4, 22, 11, 30)

    client.application.config['APPOINTMENTS'] = {
        1: [Appointment(appt_datetime)]
    }
    response = client.get('/api/appointments/1')

    expected_response = [{
        'start_time': '2021-04-22 11:30',
        'end_time': '2021-04-22 12:00',
    }]

    assert response.status_code == 200

    appointments = response.get_json()['appointments']
    assert len(appointments) == 1
    assert appointments[0]['start_time'] == expected_response[0]['start_time']
    assert appointments[0]['end_time'] == expected_response[0]['end_time']


def test_get_user_appointments_multiple(client):
    """
    Test that ALL of the user's appointments are returned
    with a GET request.
    """
    appt_datetime_1 = datetime(2021, 4, 21, 11, 30)
    appt_datetime_2 = datetime(2021, 4, 22, 11, 30)

    client.application.config['APPOINTMENTS'] = {
        1: [Appointment(appt_datetime_1), Appointment(appt_datetime_2)]
    }
    response = client.get('/api/appointments/1')

    expected_response = [
        {
            'start_time': '2021-04-21 11:30',
            'end_time': '2021-04-21 12:00',
        },
        {
            'start_time': '2021-04-22 11:30',
            'end_time': '2021-04-22 12:00',
        },
    ]

    assert response.status_code == 200

    appointments = response.get_json()['appointments']
    assert len(appointments) == 2
    assert appointments[0]['start_time'] == expected_response[0]['start_time']
    assert appointments[0]['end_time'] == expected_response[0]['end_time']
    assert appointments[1]['start_time'] == expected_response[1]['start_time']
    assert appointments[1]['end_time'] == expected_response[1]['end_time']


def test_get_user_appointments_only_specified_user(client):
    """
    Test that ONLY the specified user's appointments
    are returned with a GET request.
    """
    appt_datetime_1 = datetime(2021, 4, 21, 11, 30)
    appt_datetime_2 = datetime(2021, 4, 22, 11, 30)

    client.application.config['APPOINTMENTS'] = {
        1: [Appointment(appt_datetime_1)],
        2: [Appointment(appt_datetime_2)],
    }

    response = client.get('/api/appointments/1')

    expected_response = [{
        'start_time': '2021-04-21 11:30',
        'end_time': '2021-04-21 12:00',
    }]

    assert response.status_code == 200

    appointments = response.get_json()['appointments']
    assert len(appointments) == 1
    assert appointments[0]['start_time'] == expected_response[0]['start_time']
    assert appointments[0]['end_time'] == expected_response[0]['end_time']


def test_get_user_appointments_overnight(client):
    """
    Test that the user's appointments are returned
    with a GET request.
    """
    appt_datetime = datetime(2021, 4, 22, 23, 30)

    client.application.config['APPOINTMENTS'] = {
        1: [Appointment(appt_datetime)]
    }
    response = client.get('/api/appointments/1')

    expected_response = [{
        'start_time': '2021-04-22 23:30',
        'end_time': '2021-04-23 00:00',
    }]

    assert response.status_code == 200

    appointments = response.get_json()['appointments']
    assert len(appointments) == 1
    assert appointments[0]['start_time'] == expected_response[0]['start_time']
    assert appointments[0]['end_time'] == expected_response[0]['end_time']


def test_add_user_appointments(client):
    """
    Test that the new appointment is created and returned
    with a POST request.
    """
    appt_datetime = datetime(2021, 4, 22, 11, 30)

    response = client.post(
        '/api/appointments/1',
        json={'appointment': str(appt_datetime)}
    )

    expected_response = {
        'start_time': '2021-04-22 11:30',
        'end_time': '2021-04-22 12:00',
    }

    assert response.status_code == 201
    assert response.json['start_time'] == expected_response['start_time']
    assert response.json['end_time'] == expected_response['end_time']


def test_add_user_appointments_fails_invalid_datetime(client):
    """
    Test that a 400 status code is returned when
    a user attempts to schedule a new appointment via
    a POST request with an invalid datetime string as input.
    """
    response = client.post(
        '/api/appointments/1',
        json={'appointment': 'BAD_INPUT'}
    )

    assert response.status_code == 400
    assert response.json['message'] == 'Appointments must be a valid datetime'


def test_add_user_appointments_fails_wrong_time(client):
    """
    Test that a 400 status code is returned when
    a user attempts to schedule a new appointment via
    a POST request with a time that does not start
    on the hour or half-hour.
    """
    appt_datetime = datetime(2021, 4, 22, 11, 3)

    response = client.post(
        '/api/appointments/1',
        json={'appointment': str(appt_datetime)}
    )

    assert response.status_code == 400
    assert response.json['message'] == 'Appointments must start on the hour or half hour'


def test_add_user_appointments_fails_already_scheduled_for_day(client):
    """
    Test that a 400 status code is returned when
    a user attempts to schedule a new appointment via
    a POST request when the user already has an
    existing appointment scheduled for the same day.
    """
    appt_datetime = datetime(2021, 4, 22, 11, 30)

    client.post(
        '/api/appointments/1',
        json={'appointment': str(appt_datetime)}
    )

    response = client.post(
        '/api/appointments/1',
        json={'appointment': str(appt_datetime)}
    )

    assert response.status_code == 400
    assert response.json['message'] == 'User already has an appointment scheduled for this calendar date'


def test_add_user_appointments_fails_already_scheduled_for_day_overlap(client):
    """
    Test that a 400 status code is returned when
    a user attempts to schedule a new appointment via
    a POST request when an already existing appointment
    starts on the previous day, but ends on the day
    of the new appointment.
    """
    first_appt_datetime = datetime(2021, 4, 22, 23, 30)

    client.post(
        '/api/appointments/1',
        json={'appointment': str(first_appt_datetime)}
    )

    response = client.get('/api/appointments/1')
    expected_response = [{
        'start_time': '2021-04-22 23:30',
        'end_time': '2021-04-23 00:00',
    }]

    assert response.status_code == 200

    appointments = response.get_json()['appointments']
    assert len(appointments) == 1
    assert appointments[0]['start_time'] == expected_response[0]['start_time']
    assert appointments[0]['end_time'] == expected_response[0]['end_time']

    second_appt_datetime = datetime(2021, 4, 22, 23, 30)
    response = client.post(
        '/api/appointments/1',
        json={'appointment': str(second_appt_datetime)}
    )

    assert response.status_code == 400
    assert response.json['message'] == 'User already has an appointment scheduled for this calendar date'
