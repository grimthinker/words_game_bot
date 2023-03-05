FROM python:3.10


COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app app
COPY config.yml .
COPY main.py .
EXPOSE 9080
