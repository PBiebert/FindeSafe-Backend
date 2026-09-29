# Basisimage: schlankes Python, passend zur lokalen Version (3.14)
FROM python:3.14-slim

# PYTHONDONTWRITEBYTECODE: keine .pyc-Dateien im Container schreiben
# PYTHONUNBUFFERED: Logs sofort ausgeben (sichtbar über "docker logs")
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Arbeitsverzeichnis im Container
WORKDIR /app

# Zuerst nur requirements.txt kopieren und installieren:
# Docker cached diese Schicht, solange sich die Abhängigkeiten nicht ändern.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Danach den restlichen Code kopieren (ändert sich häufig, daher nach pip install)
COPY . .

# Startskript ausführbar machen (collectstatic, migrate und Superuser
# laufen beim Start des Containers, siehe backend.entrypoint.sh)
RUN chmod +x /app/backend.entrypoint.sh

# Sicherheit: Die App soll nicht als root laufen. Falls ein Angreifer über eine
# Sicherheitslücke Code im Container ausführen kann, hat er sonst volle Rechte.
# Neuen Benutzer "appuser" mit eigenem Home-Verzeichnis anlegen
RUN useradd --create-home appuser
# Dem neuen Benutzer den Besitz am Code in /app übertragen.
RUN chown -R appuser /app
# Als appuser statt root arbeiten.
USER appuser

# Dokumentiert den Port, auf dem die Anwendung lauscht
EXPOSE 8000

# Das Skript läuft bei jedem Start zuerst und übergibt danach an den CMD
# (bzw. an den command: aus der docker-compose.yml)
ENTRYPOINT ["/app/backend.entrypoint.sh"]

# Produktionsserver gunicorn statt Django-Dev-Server:
# core.wsgi:application = WSGI-Einstiegspunkt des Projekts (core/wsgi.py)
# --bind 0.0.0.0:8000   = auf allen Interfaces lauschen, damit der Port von außen erreichbar ist
# --workers 3           = drei parallele Worker-Prozesse
# --access-logfile -    = Zugriffslogs auf stdout, sichtbar in "docker compose logs"
CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--access-logfile", "-"]
