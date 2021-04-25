FROM python:3.9.4-alpine

LABEL maintainer="howe1rp@gmail.com"

COPY ./src /app
COPY ./requirements.txt /requirements.txt

RUN pip install -r requirements.txt

WORKDIR /app

EXPOSE 5000

ENTRYPOINT ["python"]
CMD ["app.py"]