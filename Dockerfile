FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .

RUN apt-get update && \
    apt-get install -y gcc && \
    pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get remove -y gcc && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

COPY . .
EXPOSE 3000
CMD ["gunicorn", "app:app", "-b", "0.0.0.0:8080"]
