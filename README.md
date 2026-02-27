# Urbanism Website

Leichtgewichtige Band-Webseite mit:
- Neon-Website mit mehreren Unterseiten
- Social-Links (Instagram, YouTube, Spotify)
- Tourdaten auf eigener Konzertseite (kommend + vergangen)
- Booking-Seite für Veranstalter
- Mini-Adminbereich zum Pflegen der Shows

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Optional in `.env` anpassen:
- `SECRET_KEY`
- `ADMIN_PASSWORD`

## Start

```bash
source .venv/bin/activate
export $(grep -v '^#' .env | xargs)
python app.py
```

Dann öffnen: [http://127.0.0.1:5000](http://127.0.0.1:5000)

## Admin

- Login: [http://127.0.0.1:5000/admin/login](http://127.0.0.1:5000/admin/login)
- Standardpasswort (nur lokal): `urbanism-admin`
- Bitte für Deployment unbedingt ändern (`ADMIN_PASSWORD`)

## Inhalte anpassen

- Bilder liegen unter `static/images/photos/` und werden automatisch auf der Startseite angezeigt.
- Logo-Dateien liegen unter `static/images/logos/`.
- Quell-Assets sind separat unter `assets/photos/` und `assets/logos/` organisiert.
- Zum Austauschen von Bildern einfach Dateien in `static/images/photos/` ersetzen (Logo bleibt getrennt).
- Neue Bilder kannst du auch direkt in `assets/photos/` legen: sie werden beim Seitenaufruf automatisch nach `static/images/photos/` synchronisiert und in der Galerie angezeigt.

## Datenhaltung

Die Shows werden in einer lokalen SQLite-Datei gespeichert:
- `data.db`

Das macht die Übergabe an euren Booker einfach, solange er Zugriff auf dieselbe Deployment-Instanz hat.
