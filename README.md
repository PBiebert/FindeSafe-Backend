# FindeSafe-Backend

Backend (Django + Django REST Framework) für die FindeSafe-App (React Native/Expo,
separates Repo). Die App ermöglicht Standortabfragen, das Teilen des Standorts mit
festgelegten Personen und das gleichzeitige Auslösen eines Alerts.
Zielgruppe: Privatnutzer in Deutschland aller Altersgruppen.

## Tech-Stack

- Python, Django, Django REST Framework
- PostgreSQL (Treiber `psycopg`), Redis (Hintergrund-Jobs mit Django RQ)
- Docker / Docker Compose (Services `web`, `worker`, `db`, `redis`)
- gunicorn (Produktionsserver), WhiteNoise (statische Dateien)
- `python-dotenv` zum Laden der `.env`

Das Projekt wird vollständig in Docker entwickelt und betrieben.

## Voraussetzungen

- Docker und Docker Compose (`docker --version`, `docker compose version`)
- Python 3.14+ und pip nur lokal, um Abhängigkeiten in `requirements.txt` zu pflegen
  (siehe [Abhängigkeiten pflegen](#abhängigkeiten-pflegen))

## Installation & Konfiguration

1. Repository klonen:

   ```bash
   git clone <repo-url>
   cd BE-FindeSafe
   ```

2. `.env` aus der Vorlage anlegen und ausfüllen (Beschreibung der Variablen siehe
   [Umgebungsvariablen](#umgebungsvariablen)):

   ```bash
   cp .env.template .env
   ```

   - Alle Platzhalter in der `.env`, die mit `<` beginnen und mit `>` enden, durch eigene Werte ersetzen.
   - Werte ohne Anführungszeichen und ohne Leerzeichen um das `=` schreiben.
   - In Passwörtern kein `$` und kein `#` verwenden (`$` deutet Docker Compose als
     Variable, `#` beginnt einen Kommentar).
   - `REDIS_HOST` muss `redis` und `DB_HOST` muss `db` bleiben (Servicenamen aus
     der `docker-compose.yml`).

3. Container bauen und starten:

   ```bash
   docker compose up --build
   ```

   Das Startskript `backend.entrypoint.sh` sammelt beim Start des Webservers
   die statischen Dateien, führt die Migrationen aus und legt den Superuser aus
   der `.env` an.

4. Prüfen, ob alles läuft:

   - Im Log von `web` erscheint `Starting gunicorn`, im Log von `worker`
     `Listening on default...`.
   - `http://localhost:8000/admin/` zeigt die Login-Seite. Anmelden mit
     `DJANGO_SUPERUSER_EMAIL` und `DJANGO_SUPERUSER_PASSWORD` aus der `.env`.
   - Der Alltag mit den Containern (Stoppen, Logs, Migrationen usw.) steht unter
     [Entwicklung](#entwicklung).

## Umgebungsvariablen

Werden in `core/settings.py` über `python-dotenv` aus der `.env` geladen.
Werte werden vom Entwickler selbst eingepflegt.

| Variable                    | Beschreibung                                                         | Default                                       |
| --------------------------- | -------------------------------------------------------------------- | --------------------------------------------- |
| `SECRET_KEY`                | Django Secret Key                                                    | –                                             |
| `DEBUG`                     | Debug-Modus (`True`/`False`)                                         | `False`                                       |
| `ALLOWED_HOSTS`             | Kommagetrennte Hosts (für LAN-Zugriff die LAN-IP ergänzen)           | `localhost`                                   |
| `EMAIL_BACKEND`             | Django E-Mail-Backend                                                | `django.core.mail.backends.smtp.EmailBackend` |
| `EMAIL_HOST`                | SMTP-Host                                                            | –                                             |
| `EMAIL_PORT`                | SMTP-Port                                                            | `587`                                         |
| `EMAIL_USE_TLS`             | TLS verwenden (`True`/`False`)                                       | `True`                                        |
| `EMAIL_USE_SSL`             | SSL verwenden (`True`/`False`)                                       | `False`                                       |
| `EMAIL_HOST_USER`           | SMTP-Benutzer                                                        | –                                             |
| `EMAIL_HOST_PASSWORD`       | SMTP-Passwort                                                        | –                                             |
| `DEFAULT_FROM_EMAIL`        | Absenderadresse                                                      | Wert von `EMAIL_HOST_USER`                    |
| `REDIS_HOST`                | Host des Redis-Servers (in Docker der Servicename `redis`)           | `localhost`                                   |
| `REDIS_PORT`                | Port des Redis-Servers                                               | `6379`                                        |
| `REDIS_DB`                  | Redis-Datenbank-Index                                                | `0`                                           |
| `REDIS_PASSWORD`            | Passwort des Redis-Servers (Redis startet damit per `--requirepass`) | – (leer)                                      |
| `DB_NAME`                   | Name der PostgreSQL-Datenbank (wird beim ersten Start angelegt)      | –                                             |
| `DB_USER`                   | PostgreSQL-Benutzer (Superuser der Datenbank)                        | –                                             |
| `DB_PASSWORD`               | Passwort des PostgreSQL-Benutzers                                    | –                                             |
| `DB_HOST`                   | Host der Datenbank (in Docker der Servicename `db`)                  | `db`                                          |
| `DB_PORT`                   | Port der Datenbank                                                   | `5432`                                        |
| `DJANGO_SUPERUSER_EMAIL`    | E-Mail des Admin-Users (Login), wird beim Start angelegt             | –                                             |
| `DJANGO_SUPERUSER_USERNAME` | Username des Admin-Users (Pflichtfeld des User-Modells)              | –                                             |
| `DJANGO_SUPERUSER_PASSWORD` | Passwort des Admin-Users                                             | –                                             |

Hinweise zu einzelnen Variablen:

- **`SECRET_KEY`:** Einen langen Zufallswert verwenden, z. B. erzeugt mit
  `openssl rand -base64 48`. Pro Umgebung einen eigenen Wert.
- **`ALLOWED_HOSTS`:** Nur Hostnamen bzw. IPs ohne Port, z. B.
  `localhost,127.0.0.1,192.168.178.20`.
- **`EMAIL_USE_TLS` / `EMAIL_USE_SSL`:** Genau eines auf `True` setzen
  (Port 587 mit TLS, Port 465 mit SSL).
- **`EMAIL_BACKEND`:** Zum Testen ohne Mailserver
  `django.core.mail.backends.console.EmailBackend` setzen. Die Mails erscheinen
  dann im Log des Workers (`docker compose logs -f worker`).
- **`REDIS_HOST` / `DB_HOST`:** In Docker die Servicenamen `redis` bzw. `db`,
  nicht `localhost` (im Container wäre das der Container selbst).
- **`DB_*`:** Datenbank und Benutzer werden beim ersten Start des Volumes
  `postgres_data` angelegt. Spätere Änderungen wirken nicht auf eine bestehende
  Datenbank. Zurücksetzen mit `docker compose down -v` (löscht alle Daten).
  `DB_USER` ist in der Datenbank ein Superuser.
- **`DJANGO_SUPERUSER_*`:** Der Admin-Benutzer wird beim ersten Start angelegt,
  Login unter `/admin/` mit E-Mail und Passwort. Ein neues Passwort setzt man
  später mit `docker compose exec web python manage.py changepassword <email>`.

## Entwicklung

Das Projekt besteht aus vier Services: `web` (Django mit gunicorn), `worker`
(RQ-Worker für Hintergrund-Jobs, z. B. den Versand der Bestätigungs-E-Mails, läuft
mit demselben Image), `db` (PostgreSQL) und `redis`.

### Container starten und stoppen

```bash
# Alle Services bauen und starten
docker compose up --build

# Im Hintergrund starten
docker compose up -d --build

# Stoppen (Daten im Volume postgres_data bleiben erhalten)
docker compose down

# Stoppen und Datenbank komplett löschen (Achtung: alle Daten gehen verloren)
docker compose down -v
```

- Der Code wird beim Bauen ins Image kopiert. Nach Codeänderungen ist ein
  `docker compose up --build` nötig.
- Die API ist im LAN erreichbar (Port 8000 wird veröffentlicht). Die LAN-IP
  muss dafür in `ALLOWED_HOSTS` in der `.env` stehen.

### Logs und Status

```bash
# Logs der Services ansehen (auch: db, redis)
docker compose logs -f web
docker compose logs -f worker

# Status der Container prüfen
docker compose ps
```

### Datenbank und Migrationen

```bash
# Migrationen erstellen / anwenden (Container müssen laufen)
docker compose exec web python manage.py makemigrations
docker compose exec web python manage.py migrate

# Einmaliger Befehl in einem neuen Container (wenn nichts läuft)
docker compose run --rm web python manage.py migrate
```

### Konsole im Container

```bash
# Django Shell (z. B. um E-Mail-Templates ad-hoc zu rendern/prüfen)
docker compose exec web python manage.py shell

# Konsole im web-Container öffnen (dort die Befehle ohne "docker compose exec web" ausführen,
# z. B. "python manage.py migrate"; mit "exit" wieder verlassen)
docker compose exec web bash
```

Alternativ in Docker Desktop den Container `web` auswählen und den Reiter
**Exec** öffnen.

### Abhängigkeiten pflegen

Die Pakete stehen in `requirements.txt` und werden beim Bauen ins Image
installiert. Die lokale virtuelle Umgebung ist optional und dient dem Editor
(Autovervollständigung, Linter) sowie `pip freeze`:

```bash
python -m venv .venv
source .venv/bin/activate        # Mac/Linux
.venv\Scripts\activate           # Windows
pip install -r requirements.txt
```

Nach dem Hinzufügen/Aktualisieren einer Abhängigkeit muss das Image neu gebaut werden:

```bash
pip install <paket>
pip freeze > requirements.txt
docker compose up --build
```

## Tests

Die Tests basieren auf `unittest` (Django-Testrunner), nicht auf pytest.

```bash
# Alle Tests (im laufenden web-Container)
docker compose exec web python manage.py test

# Einzelnes Modul / einzelne Klasse / einzelner Test
docker compose exec web python manage.py test accounts.tests.test_registration
docker compose exec web python manage.py test accounts.tests.test_registration.RegisterTest.test_post_register_valid_data_return_201
```

Django legt für die Tests eine eigene Datenbank `test_<DB_NAME>` an (der
DB-Benutzer braucht dafür das Recht `CREATEDB`).

## API-Endpoints

Alle App-Routen liegen unter `/api/` (`core/urls.py` → `accounts/api/urls.py`).

| Methode | Pfad                             | View                         | Beschreibung                                                                                                                                                                                                                                     |
| ------- | -------------------------------- | ---------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `POST`  | `/api/register/`                 | `RegisterView`               | Registrierung. Body: `email`, `password`, `confirm_password`, `first_name`, `last_name`, `agb_accepted`, `privacy_accepted`. Legt User mit `is_active=False` an und erzeugt einen 6-stelligen Verifizierungscode (5 Min. gültig). Antwort `201`. |
| `POST`  | `/api/account-verification/`     | `AccountActivateView`        | Kontoaktivierung. Body: `email`, `code`. Max. 3 Fehlversuche, danach wird der Code gelöscht und muss neu angefordert werden. Antwort `200`.                                                                                                      |
| `POST`  | `/api/resend-verification-code/` | `ResendVerificationCodeView` | Neuen Verifizierungscode anfordern                                                                                                                                                                                                               |
| –       | `/admin/`                        | Django Admin                 | Admin-Oberfläche                                                                                                                                                                                                                                 |
| –       | `/django-rq/`                    | Django RQ                    | Dashboard für Hintergrund-Jobs (laufend/erledigt/fehlgeschlagen)                                                                                                                                                                                 |

## Projektstruktur

```
.
├── core/                  # Projekt-Settings, Root-URLs, ASGI/WSGI
├── accounts/              # CustomUser (Login per E-Mail), Registrierung & Verifizierung
│   ├── api/               # serializers, views, urls, services (E-Mail-Versand)
│   ├── services.py        # Domain-Logik (z. B. Verifizierungscode erzeugen)
│   ├── templates/app/     # E-Mail-Templates (base_email.html, activation_email.html)
│   ├── migrations/
│   └── tests/
├── backend.Dockerfile     # Image: Python, Abhängigkeiten, Code, Start als appuser
├── backend.entrypoint.sh  # Start: collectstatic, migrate, Superuser, dann gunicorn
├── docker-compose.yml     # Services: web, worker, db (PostgreSQL), redis
├── .dockerignore          # Was nicht ins Image kopiert wird (u. a. .env)
├── .env.template          # Vorlage der Umgebungsvariablen (Kopie: .env, nicht im Repo)
├── manage.py
└── requirements.txt
```

Neue Apps folgen demselben Aufbau `<app>/api/{serializers,views,urls,services}.py` wie `accounts`.
