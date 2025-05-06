FROM python:3.12.2
WORKDIR /app

COPY certs/freeipa-lame.crt /app/freeipa-lame.crt

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV REQUESTS_CA_BUNDLE=/app/freeipa-lame.crt
ENV SSL_CERT_FILE=/app/freeipa-lame.crt

EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "minio_app.wsgi:application"]
