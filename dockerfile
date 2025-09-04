FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN apt-get update && apt-get install -y gcc libffi-dev python3-dev && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir -r requirements.txt

COPY voice_monitor.py .

ENV CHECK_INTERVAL=60
ENV PROM_PORT=9100

EXPOSE 9100

CMD ["python", "voice_monitor.py"]
