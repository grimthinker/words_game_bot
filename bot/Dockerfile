FROM python:3.10


COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app app
COPY alembic alembic
COPY config.yml .
COPY main.py .
COPY pytest.ini .
COPY alembic.ini .
EXPOSE 9090
