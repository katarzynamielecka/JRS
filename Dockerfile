FROM python:3.11

# Wyłączenie buforowania wyjścia w Pythonie
ENV PYTHONUNBUFFERED=1

# Ustawienie katalogu roboczego
WORKDIR /code

# Instalacja wymaganych certyfikatów CA (dla obsługi SSL)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl \
    && update-ca-certificates \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Kopiowanie pliku requirements.txt i instalacja zależności
COPY requirements.txt /code/
RUN pip install --no-cache-dir -r requirements.txt

# Pobranie skryptu `wait-for-it` i nadanie mu uprawnień do uruchamiania
ADD https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh /wait-for-it.sh
RUN chmod +x /wait-for-it.sh

# Kopiowanie całego kodu aplikacji
COPY . /code/

# Dodanie informacji o certyfikatach dla Pythona
ENV SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt

# Komenda startowa
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
