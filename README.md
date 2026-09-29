# FindeSafe-Backend

Backend (Django + Django REST Framework) für die FindeSafe-App (React Native/Expo,
separates Repo). Die App ermöglicht Standortabfragen, das Teilen des Standorts mit
festgelegten Personen und das gleichzeitige Auslösen eines Alerts.
Zielgruppe: Privatnutzer in Deutschland aller Altersgruppen.

## Tech-Stack

- Python, Django, Django REST Framework
- SQLite (lokale Entwicklung), PostgreSQL (Veröffentlichung, geplant)
- Redis, Docker (geplant)
- `python-dotenv` zum Laden der `.env`

## Voraussetzungen

- Python 3.14+
- pip 26.1.1+

---

## Installation & Konfiguration

1. Repository klonen:

   ```bash
   git clone <repo-url>
   cd BE-FindeSafe
   ```

2. Virtuelle Umgebung erstellen und aktivieren:

   ```bash
   python -m venv .venv
   source .venv/bin/activate        # Mac/Linux
   .venv\Scripts\activate           # Windows
   ```

3. Abhängigkeiten installieren:

   ```bash
   pip install -r requirements.txt
   ```

   Nach dem Hinzufügen/Aktualisieren einer Abhängigkeit:

   ```bash
   pip freeze > requirements.txt
   ```

4. `.env` im Projekt-Root anlegen (siehe [Umgebungsvariablen](#umgebungsvariablen)).

5. Datenbank migrieren:

   ```bash
   python manage.py migrate
   ```

## Umgebungsvariablen

Werden in `core/settings.py` über `python-dotenv` aus der `.env` geladen.
Werte werden vom Entwickler selbst eingepflegt.

| Variable              | Beschreibung                                                   | Default                                          |
| --------------------- | -------------------------------------------------------------- | ------------------------------------------------ |
| `SECRET_KEY`          | Django Secret Key                                              | –                                                |
| `DEBUG`               | Debug-Modus (`True`/`False`)                                   | `False`                                          |
| `ALLOWED_HOSTS`       | Kommagetrennte Hosts (für LAN-Zugriff die LAN-IP ergänzen)     | `localhost`                                      |
| `EMAIL_BACKEND`       | Django E-Mail-Backend                                          | `django.core.mail.backends.smtp.EmailBackend`    |
| `EMAIL_HOST`          | SMTP-Host                                                      | –                                                |
| `EMAIL_PORT`          | SMTP-Port                                                      | `587`                                            |
| `EMAIL_USE_TLS`       | TLS verwenden (`True`/`False`)                                 | `True`                                           |
| `EMAIL_USE_SSL`       | SSL verwenden (`True`/`False`)                                 | `False`                                          |
| `EMAIL_HOST_USER`     | SMTP-Benutzer                                                  | –                                                |
| `EMAIL_HOST_PASSWORD` | SMTP-Passwort                                                  | –                                                |
| `DEFAULT_FROM_EMAIL`  | Absenderadresse                                                | Wert von `EMAIL_HOST_USER`                       |
| `REDIS_HOST`          | Host des Redis-Servers (für Django RQ / Hintergrund-Jobs)      | `localhost`                                       |
| `REDIS_PORT`          | Port des Redis-Servers                                         | `6379`                                            |
| `REDIS_DB`            | Redis-Datenbank-Index                                          | `0`                                                |
| `REDIS_PASSWORD`      | Passwort des Redis-Servers                                     | – (leer)                                          |

## Entwicklung

```bash
# Server starten
python manage.py runserver

# Server im LAN erreichbar machen (z. B. für Tests auf dem Handy;
# LAN-IP in ALLOWED_HOSTS in der .env ergänzen)
python manage.py runserver 0.0.0.0:8000

# Migrationen erstellen / anwenden
python manage.py makemigrations
python manage.py migrate

# Django Shell (z. B. um E-Mail-Templates ad-hoc zu rendern/prüfen)
python manage.py shell

# RQ-Worker starten (verarbeitet Hintergrund-Jobs, z. B. den Versand der
# Bestätigungs-E-Mails; benötigt einen laufenden Redis-Server)
python manage.py rqworker default
```

Formatierung: Black (`.vscode/settings.json` führt es beim Speichern für Python-Dateien aus).

## Tests

Die Tests basieren auf `unittest` (Django-Testrunner), nicht auf pytest.

```bash
# Alle Tests
python manage.py test

# Einzelnes Modul / einzelne Klasse / einzelner Test
python manage.py test accounts.tests.test_registration
python manage.py test accounts.tests.test_registration.RegisterTest.test_post_register_valid_data_return_201
```

## API-Endpoints

Alle App-Routen liegen unter `/api/` (`core/urls.py` → `accounts/api/urls.py`).

| Methode | Pfad                             | View                         | Beschreibung                                                                                                                                                                                         |
| ------- | -------------------------------- | ---------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `POST`  | `/api/register/`                 | `RegisterView`               | Registrierung. Body: `email`, `password`, `confirm_password`, `first_name`, `last_name`, `agb_accepted`, `privacy_accepted`. Legt User mit `is_active=False` an und erzeugt einen 6-stelligen Verifizierungscode (5 Min. gültig). Antwort `201`. |
| `POST`  | `/api/account-verification/`     | `AccountActivateView`        | Kontoaktivierung. Body: `email`, `code`. Max. 3 Fehlversuche, danach wird der Code gelöscht und muss neu angefordert werden. Antwort `200`.                                                          |
| `POST`  | `/api/resend-verification-code/` | `ResendVerificationCodeView` | Neuen Verifizierungscode anfordern                                                                                                                                                                   |
| –       | `/admin/`                        | Django Admin                 | Admin-Oberfläche                                                                                                                                                                                     |
| –       | `/django-rq/`                    | Django RQ                    | Dashboard für Hintergrund-Jobs (laufend/erledigt/fehlgeschlagen)                                                                                                                                     |

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
├── manage.py
└── requirements.txt
```

Neue Apps folgen demselben Aufbau `<app>/api/{serializers,views,urls,services}.py` wie `accounts`.
