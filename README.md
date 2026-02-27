# Urbanism Website (Static)

Statische Band-Website für lokalen Betrieb und GitHub Pages mit identischer Codebase.

## Seiten

- `index.html` (Home)
- `concerts.html` (Upcoming Shows aus Google Sheet)
- `booking.html` (Kontakt + Press Kit & Tech Rider)
- `impressum.html` (Impressum + rechtliche Hinweise)

## Lokal starten

```bash
cd /Users/andregensler/code/urbanism_website
python3 -m http.server 8000
```

Dann öffnen: [http://localhost:8000](http://localhost:8000)

## GitHub Pages Deployment

1. Repo nach GitHub pushen.
2. In GitHub: `Settings -> Pages`.
3. `Deploy from branch` aktivieren (`main` / root).
4. Optional: Custom Domain setzen.

## Upcoming Shows via Google Sheet

Die Konzerte-Seite lädt CSV direkt aus diesem veröffentlichten Sheet:

- [Google Sheet CSV](https://docs.google.com/spreadsheets/d/e/2PACX-1vSOlTEvbpt1radzheruEhEjNFKFpf1H4zI-ONorZW_UjMf4OuShE2CFZKJzti63Lj1dE3pU7eIrt_u0/pub?output=csv)

Erwartete Spalten im Sheet:

```text
show_date,title,city,venue,ticket_url,notes,active
```

Hinweise:
- `show_date` im Format `YYYY-MM-DD`
- nur kommende Shows werden angezeigt
- `active=false` blendet einen Eintrag aus

## Galerie aus Foto-Ordner

Die Gallery nutzt `static/data/gallery.json`.

Wenn du neue Bilder in `static/images/photos/` legst, aktualisiere die Manifest-Datei mit:

```bash
./scripts/generate-gallery-manifest.sh
```

Danach Commit/Push oder lokal neu laden.
