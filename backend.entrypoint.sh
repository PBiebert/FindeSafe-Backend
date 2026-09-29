#!/bin/sh
# Startskript des Containers: bereitet die Anwendung vor und startet dann den
# eigentlichen Prozess (gunicorn bzw. der RQ-Worker).

# Bei jedem Fehler sofort abbrechen, damit der Container nicht halb vorbereitet startet
set -e

# Die Vorbereitung soll nur der Webserver machen. Der Worker nutzt dasselbe Image
# und dieses Skript, würde sonst gleichzeitig migrieren und sich mit "web" in die
# Quere kommen. $1 ist das erste Wort des Startbefehls (CMD bzw. command:).
if [ "$1" = "gunicorn" ]; then
    echo "Sammle statische Dateien..."
    python manage.py collectstatic --noinput

    echo "Führe Datenbank-Migrationen aus..."
    python manage.py migrate --noinput

    # Superuser nur anlegen, wenn E-Mail und Passwort in der .env gesetzt sind.
    # createsuperuser --noinput liest DJANGO_SUPERUSER_EMAIL, DJANGO_SUPERUSER_USERNAME
    # und DJANGO_SUPERUSER_PASSWORD aus der Umgebung.
    if [ -n "$DJANGO_SUPERUSER_EMAIL" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
        echo "Lege Superuser an..."
        # Existiert der User schon (z. B. nach einem Neustart), schlägt der Befehl
        # fehl. "||" verhindert dann den Abbruch durch set -e.
        python manage.py createsuperuser --noinput || echo "Superuser existiert bereits."
    fi
fi

# Übergibt an den eigentlichen Startbefehl. "exec" ersetzt das Skript durch diesen
# Prozess, damit er PID 1 wird und Stopp-Signale (docker stop) direkt erhält.
exec "$@"
