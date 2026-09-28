# CLAUDE.md

## Projektüberblick

- Backend für React Native App (iOS/Android) um Standortabfragen zu machen und mit festgelegte personen teilen sowie gleichzeitiig Alert auslösen.
- Zielgruppe:Privatnutzer aktuell in Deutschland aller altersgruppen.
- Frontend: React Native + Expo in separates Repo.

## Tech-Stack

- Backend: Django, Django REST Framework, Python, SQLite(Lokale Entwicklung), PostgreSQL(zur Veröffentlichung), Redis, Docker

## Konventionen

- Jeder Codeblock erhält Docstrings auf Deutsch
- Kommentiere den code detailiert auf deutsch um das verständniss zu erleichtern.
- Inhaltliche Änderungen pro Antwort auf ~200–300 Zeilen und max. 2 Dateien begrenzen, bei größerem Scope in Teilschritte/Task-Prompts aufteilen, sonst wird das Gegenlesen unzuverlässig. Ausnahme: rein
  mechanische Änderungen (Umbenennungen, Formatierung).
- Du Antwortest mir immer auf deutsch
- Daten die in die .env gehören werden mir mitgeteilt und durch den Entwickler eingepflegt

## Dokumentation

- `README.md` muss immer aktuell gehalten werden. Alle wesentlichen
  notwendigen Befehle müssen fortgeschrieben werden – das betrifft
  Dinge wie Setup-Befehle, Endpoints, benötigte `.env`-Variablen (nur Namen, keine Werte) usw.

## Verbote / No-Gos

- Keine Refactorings an Code, der nicht Teil der Aufgabe ist
- Keine Automatischen Commits
- Nie selbst `git commit` ausführen
- .env darf nicht gelesen oder bearbeitet werden

## Wiederkehrende Befehle

```bash
# Setup
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip freeze > requirements.txt      # nach dem Hinzufügen/Aktualisieren einer Abhängigkeit

# Starten
python manage.py runserver
python manage.py runserver 0.0.0.0:8000   # um den Server von einem Handy/Gerät im selben LAN zu erreichen (LAN-IP in ALLOWED_HOSTS in der .env ergänzen)

# Datenbank
python manage.py makemigrations
python manage.py migrate

# Tests (basieren auf unittest, nicht pytest)
python manage.py test
python manage.py test accounts.tests.test_registration
python manage.py test accounts.tests.test_registration.RegisterTest.test_post_register_valid_data_return_201

# Django Shell (z.B. um E-Mail-Templates ad-hoc zu rendern/prüfen)
python manage.py shell
```

Formatierung: Black (`.vscode/settings.json` führt es beim Speichern für `[python]` aus).

## Architektur

**Auth-Modell:** `accounts.CustomUser` (`AUTH_USER_MODEL`) erweitert
`AbstractUser` und nutzt `email` als `USERNAME_FIELD` statt Username.
`username` ist trotzdem erforderlich (`REQUIRED_FIELDS`) und wird bei der
Erstellung auf den E-Mail-Wert gesetzt.

**Registrierungs-/Aktivierungs-Flow** (E-Mail + 6-stelliger Code, nicht
link-basiert):

1. `POST /api/register/` (`RegisterView`) — `RegisterSerializer` legt den
   User mit `is_active=False` an, danach erstellt
   `accounts.services.generate_verification_code()` einen
   `EmailVerificationCode` (6-stelliger Code, 5 Min. Gültigkeit).
2. `POST /api/account-verification/` (`AccountActivateView`) —
   `EmailVerificationSerializer` prüft den Code gegen den neuesten
   `EmailVerificationCode` zu dieser E-Mail, zählt fehlgeschlagene `attempts`
   (max. 3, danach wird der Code gelöscht und muss neu angefordert werden),
   und setzt bei Erfolg `is_active=True` und löscht den Code.
3. `POST /api/resend-verification-code/` (`ResendVerificationCodeView`) —
   noch nicht implementiert.

**Zwei `services.py`-Dateien, unterschiedliche Verantwortung, aber aktuell
nur je eine Funktion drin:**

- `accounts/services.py` — Domain-Logik auf Models (z.B. Verifizierungscode-
  Erstellung), wird von Views importiert.
- `accounts/api/services.py` — I/O-lastige Logik, die an die API-Schicht
  gebunden ist (Rendern + Versenden von E-Mails).

Die Trennung folgt dem Muster Domain-Logik vs. I/O/Infrastruktur (Domain-Code
bleibt dadurch unabhängig vom Mail-Versand testbar und wäre z.B. auch aus
einem Management-Command wiederverwendbar). Bei aktuell nur einer Funktion je
Datei ist der Nutzen davon aber noch gering — ein Merge in eine gemeinsame
`accounts/services.py` wäre beim aktuellen Umfang genauso vertretbar. Lohnt
sich als bewusste Trennung erst, sobald mehr Domain-Logik bzw. weitere
Mail-Typen dazukommen.

**E-Mail-Templates** (`accounts/templates/app/`, wird über Djangos
`APP_DIRS=True` gefunden, kein Eintrag in `TEMPLATES["DIRS"]` nötig):

- `base_email.html` — gemeinsames Layout (dunkles Theme passend zur
  Farbpalette der FindeSafe-App aus dem Frontend `src/themes/colors.ts`; Logo
  von `img.philippbiebert.de`). Tabellenbasiertes HTML, stylt aktuell über
  **CSS-Klassen in einem `<style>`-Block** (`.wrapper`, `.card`, `.header`,
  `.footer`, `.text`, `.title`, `.code-box`, ...). Bietet überschreibbare
  Blocks: `title`, `preheader`, `content`, `footer_note`.
- `activation_email.html` — `{% extends "app/base_email.html" %}`, füllt
  `content`/`footer_note` für die Aktivierungscode-Mail. Der `content`-Block
  stylt seine Elemente dagegen **inline** (`style="..."` direkt an
  `<h1>`/`<p>`/`<span>`), inkl. einer Klasse `fluid-padding` für responsives
  Mobile-Padding.

**URL-Struktur:** `core/urls.py` bindet alle App-Routen unter `/api/` über
`include("accounts.api.urls")` ein. Neue Apps folgen demselben
`<app>/api/{serializers,views,urls,services}.py`-Aufbau wie `accounts`.
