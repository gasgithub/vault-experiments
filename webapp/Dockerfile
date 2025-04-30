FROM python:3.13-slim

RUN pip3 install --upgrade pip

COPY requirements.txt /

RUN pip3 install -r /requirements.txt

COPY . /app
WORKDIR /app

EXPOSE 8080

CMD ["gunicorn","--config", "gunicorn_config.py", "app:app"]