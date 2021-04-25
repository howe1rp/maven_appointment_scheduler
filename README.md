# Maven Clinic Appointment Scheduler API
A simple service to help users schedule appointments. 

## Local Setup
This service can be run either locally using Python or with Docker.
To run locally, follow these instructions:

1. Create a new virtual environment and activate it.
   ### `conda`
   ```shell
   conda create -n maven-appt python=3.9
   conda activate maven-appt
   ```

   ### `venv`
   ```shell
   python -m venv venv
   source venv/bin/activate
   ```

2. Install requirements.
   ```shell
   python -m pip install -r requirements.txt
   ```

## How to Run

### Local
After setting up a new virtual environment described [above](#local-setup),
run:
```shell
python app.py
```

### Docker
Due to time constraints, I did not have time to post the image to Docker Hub,
but I did include `Dockerfile` and `docker-compose.yml` files
in this repository which can be used to run the app via Docker.

#### Run with `docker`
In a shell, run the following commands:

##### Build Image
```shell
docker build -t maven-appointment-scheduler:latest' .
```

##### Run Container
```shell
docker run --rm -p 5000:5000 maven-appointment-scheduler:latest
```

### Run with `docker-compose`
In a shell, simply run:
```shell
docker-compose up
```

### Testing
To run the unit tests, run the following command from the repository directory:
```shell
python -m pytest test/api_tests.py
```


## Routes
###`/api/appointments/<USER_ID>`
#### Parameters
Parameter|Type|Required|Description
---------|----|--------|-----------
USER_ID|`int`|Yes|The ID of the user.

### `GET`
#### Request
Get all appointments scheduled for the specified user.

Example:

```
http://localhost:5000/api/appointments/42`
```

#### Response
```json
{
    "appointments": [
        {
            "end_time": "2021-04-22 12:00",
            "start_time": "2021-04-22 11:30"
        }
    ]
}
```

### `POST`
#### Request
Create a new appointment for the specified user using the provided start datetime.
The appointment must:
* Be a valid datetime
* Start at the hour or half-hour
* Not occur on the same day as an already scheduled appointment for the same user

Example:
```
http://localhost:5000/api/appointments/42`
```
With the following JSON body:
```json
{
  "appointment": "2021-04-22 11:30"
}
```

#### Response
```json
{
    "end_time": "2021-04-22 12:00",
    "start_time": "2021-04-22 11:30"
}
```

## Error Handling
Due to time constraints, I handled only a few of the potential error situations:
1. The requested appointment time was not a valid `datetime` string.
2. The requested appointment time was on a day when the user already had an appointment.
3. The requested appointment time did not start on the hour or half-hour.

For all of these errors, the service will return an appropriate message and a `400` status code.

Some other errors that would need to be handled in a production application:
1. Return a `500` status code if something went wrong during the handling of the request
   that was not otherwise accounted for.
   (e.g. the wrong key was used in the `POST` request, the system crashed, etc.)
2. Return a `408` status code if the server timed out while processing the request.

## Implementation Details
### Assumptions
From the requirements:
>To keep it simple, we offer coverage 24/7/365 (including weekends and holidays) and have unlimited practitioners 
(in other words, any number of users can schedule appointments for the same time).

Another assumption I made was in relation to the requirement that
>a user can only have 1 appointment on a calendar date

To this end, if the user schedules an appointment for 11:30 PM,
the end time of the 30-minute appointment would be at midnight
the following day. If the user then tried to schedule another appointment
for some time on that next day, the service would return a `400` status
code because the user already has an appointment on that day.

For example, if the user scheduled an appointment at 11:30 PM on 4/23/2021,
the appointment would end at 00:00 on 4/24/2021. If the user then tried to schedule
another appointment at 13:00 on 4/24/2021, the service would return the `400` status
code.

### Datetime
To handle date logic, I opted to use Python's internal `datetime` library
with the addition of the `python-dateutil` package to easily
handle parsing date strings from the requests into `datetime` objects.

### User ID
For the User ID, I went with an integer to keep it simple.
In a production application, we may want to go with a UUID depending on the scale we want to handle.

### Database
To keep within the time constraints, I used a simple `dict` to store
the appointments rather than a database. This comes with the
restriction that the appointments do not persist across restarts.

Obviously, this isn't something that would ever make it out of the POC stage, 
but it served the purpose here. In a "real" app, we would use a database
like PostgreSQL or something similar.