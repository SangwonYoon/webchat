FROM python:3.10.13

WORKDIR /app

COPY main.py /app
COPY message.py /app
COPY requirements.txt /app

RUN python -m pip install --upgrade pip; pip install -r /app/requirements.txt

ENTRYPOINT ["python", "/app/main.py"]