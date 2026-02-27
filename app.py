from __future__ import annotations

import os
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

from flask import Flask, flash, g, redirect, render_template, request, session, url_for

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data.db"
PHOTOS_DIR = BASE_DIR / "static" / "images" / "photos"
ASSETS_PHOTOS_DIR = BASE_DIR / "assets" / "photos"

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "change-this-in-production")
app.config["ADMIN_PASSWORD"] = os.environ.get("ADMIN_PASSWORD", "urbanism-admin")
app.config["SHOWS_CSV_URL"] = os.environ.get("SHOWS_CSV_URL", "https://docs.google.com/spreadsheets/d/e/2PACX-1vSOlTEvbpt1radzheruEhEjNFKFpf1H4zI-ONorZW_UjMf4OuShE2CFZKJzti63Lj1dE3pU7eIrt_u0/pub?output=csv")

SOCIAL_LINKS = [
    {
        "name": "Instagram",
        "url": "https://www.instagram.com/urbanismband",
        "icon": "bi-instagram",
        "class": "brand-instagram",
    },
    {
        "name": "YouTube",
        "url": "https://www.youtube.com/@urbanism2189",
        "icon": "bi-youtube",
        "class": "brand-youtube",
    },
    {
        "name": "Spotify",
        "url": "https://open.spotify.com/intl-de/artist/4f0oHoowwGmDo0QQyPyRIv?si=072f0c1e39ac46f1",
        "icon": "bi-spotify",
        "class": "brand-spotify",
    },
]

GALLERY_PLACEHOLDERS = [
    {
        "src": "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?auto=format&fit=crop&w=1200&q=80",
        "alt": "Concert stage lights in neon colors",
    },
    {
        "src": "https://images.unsplash.com/photo-1492684223066-81342ee5ff30?auto=format&fit=crop&w=1200&q=80",
        "alt": "Audience at a night concert",
    },
    {
        "src": "https://images.unsplash.com/photo-1501386761578-eac5c94b800a?auto=format&fit=crop&w=1200&q=80",
        "alt": "Synthesizer keys close-up",
    },
]


def get_db() -> sqlite3.Connection:
    if "db" not in g:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        g.db = conn
    return g.db


@app.teardown_appcontext
def close_db(_: object) -> None:
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db() -> None:
    db = sqlite3.connect(DB_PATH)
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS shows (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            city TEXT NOT NULL,
            venue TEXT NOT NULL,
            show_date TEXT NOT NULL,
            ticket_url TEXT,
            notes TEXT,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    db.commit()
    seed_demo_shows(db)
    db.close()


def seed_demo_shows(db: sqlite3.Connection) -> None:
    row = db.execute("SELECT COUNT(*) AS count FROM shows").fetchone()
    if row[0] > 0:
        return

    demo_shows = [
        (
            "Urbanism - Neon Nights",
            "Berlin",
            "Lido",
            "2026-04-10",
            "https://example.com/tickets/berlin",
            "Special Guest: The Static Hearts",
        ),
        (
            "Urbanism - Electric Hearts Tour",
            "Hamburg",
            "Molotow",
            "2026-05-15",
            "https://example.com/tickets/hamburg",
            "Einlass 19:00, Start 20:00",
        ),
        (
            "Urbanism - City Lights Session",
            "Köln",
            "Artheater",
            "2026-06-05",
            "",
            "Tickets folgen in Kürze",
        ),
        (
            "Urbanism - Midnight Frequency",
            "München",
            "Backstage Club",
            "2025-11-08",
            "",
            "Support für Northern Aurora",
        ),
        (
            "Urbanism - Summer by the River",
            "Leipzig",
            "Werk 2",
            "2025-08-22",
            "",
            "Open Air Set",
        ),
        (
            "Urbanism - Retro Future Live",
            "Dresden",
            "GrooveStation",
            "2025-04-19",
            "",
            "",
        ),
    ]

    db.executemany(
        """
        INSERT INTO shows (title, city, venue, show_date, ticket_url, notes)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        demo_shows,
    )
    db.commit()


def is_admin_logged_in() -> bool:
    return bool(session.get("is_admin"))


def parse_date(date_text: str) -> datetime:
    return datetime.strptime(date_text, "%Y-%m-%d")


def sync_gallery_assets() -> None:
    PHOTOS_DIR.mkdir(parents=True, exist_ok=True)
    if not ASSETS_PHOTOS_DIR.exists():
        return

    for source in ASSETS_PHOTOS_DIR.iterdir():
        if not source.is_file() or source.name.startswith("."):
            continue

        target = PHOTOS_DIR / source.name
        should_copy = (
            not target.exists()
            or source.stat().st_mtime > target.stat().st_mtime
            or source.stat().st_size != target.stat().st_size
        )
        if should_copy:
            shutil.copy2(source, target)


def load_gallery_images() -> list[dict[str, str]]:
    sync_gallery_assets()
    files = sorted(PHOTOS_DIR.glob("*"))
    allowed_suffixes = {".jpg", ".jpeg", ".png", ".webp"}
    local_images: list[dict[str, str]] = []

    for file in files:
        if file.suffix.lower() not in allowed_suffixes:
            continue

        alt_text = file.stem.replace("_", " ").replace("-", " ").strip()
        local_images.append(
            {
                "src": f"/static/images/photos/{quote(file.name)}",
                "alt": f"Urbanism Foto: {alt_text}",
            }
        )

    return local_images or GALLERY_PLACEHOLDERS


def fetch_shows() -> tuple[list[sqlite3.Row], list[sqlite3.Row]]:
    db = get_db()
    rows = db.execute(
        """
        SELECT id, title, city, venue, show_date, ticket_url, notes
        FROM shows
        ORDER BY show_date ASC
        """
    ).fetchall()

    today = datetime.now().date()
    upcoming: list[sqlite3.Row] = []
    past: list[sqlite3.Row] = []

    for row in rows:
        show_day = parse_date(row["show_date"]).date()
        if show_day >= today:
            upcoming.append(row)
        else:
            past.append(row)

    past.reverse()
    return upcoming, past


init_db()


@app.route("/")
def index() -> str:
    gallery = load_gallery_images()
    return render_template(
        "index.html",
        social_links=SOCIAL_LINKS,
        gallery=gallery,
        hero_image=gallery[0]["src"],
        show_public_nav=True,
        active_page="home",
    )


@app.route("/konzerte")
def concerts() -> str:
    return render_template(
        "concerts.html",
        shows_csv_url=app.config["SHOWS_CSV_URL"],
        show_public_nav=True,
        active_page="concerts",
    )


@app.route("/booking")
def booking() -> str:
    return render_template(
        "booking.html",
        booking_image="/static/images/photos/DSC_5221.jpg",
        show_public_nav=True,
        active_page="booking",
    )


@app.route("/impressum")
def impressum() -> str:
    return render_template("impressum.html", show_public_nav=True, active_page="")


@app.route("/rechtliches")
def rechtliches() -> str:
    return redirect(url_for("impressum"))


@app.route("/datenschutz")
def datenschutz() -> str:
    return redirect(url_for("impressum"))


@app.route("/agb")
def agb() -> str:
    return redirect(url_for("impressum"))


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login() -> str:
    if request.method == "POST":
        password = request.form.get("password", "")
        if password == app.config["ADMIN_PASSWORD"]:
            session["is_admin"] = True
            flash("Login erfolgreich.", "success")
            return redirect(url_for("admin_shows"))
        flash("Falsches Passwort.", "error")

    return render_template("admin_login.html")


@app.route("/admin/logout")
def admin_logout() -> str:
    session.clear()
    flash("Du wurdest ausgeloggt.", "success")
    return redirect(url_for("index"))


@app.route("/admin/shows", methods=["GET", "POST"])
def admin_shows() -> str:
    if not is_admin_logged_in():
        return redirect(url_for("admin_login"))

    db = get_db()

    if request.method == "POST":
        action = request.form.get("action")

        if action == "create":
            title = request.form.get("title", "").strip()
            city = request.form.get("city", "").strip()
            venue = request.form.get("venue", "").strip()
            show_date = request.form.get("show_date", "").strip()
            ticket_url = request.form.get("ticket_url", "").strip()
            notes = request.form.get("notes", "").strip()

            if not title or not city or not venue or not show_date:
                flash("Bitte Titel, Stadt, Venue und Datum ausfüllen.", "error")
            else:
                try:
                    parse_date(show_date)
                except ValueError:
                    flash("Datum muss im Format YYYY-MM-DD sein.", "error")
                else:
                    db.execute(
                        """
                        INSERT INTO shows (title, city, venue, show_date, ticket_url, notes)
                        VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        (title, city, venue, show_date, ticket_url or None, notes or None),
                    )
                    db.commit()
                    flash("Show hinzugefügt.", "success")
                    return redirect(url_for("admin_shows"))

        elif action == "update":
            show_id = request.form.get("show_id", "").strip()
            title = request.form.get("title", "").strip()
            city = request.form.get("city", "").strip()
            venue = request.form.get("venue", "").strip()
            show_date = request.form.get("show_date", "").strip()
            ticket_url = request.form.get("ticket_url", "").strip()
            notes = request.form.get("notes", "").strip()

            if not show_id:
                flash("Show-ID fehlt.", "error")
            elif not title or not city or not venue or not show_date:
                flash("Bitte alle Pflichtfelder ausfüllen.", "error")
            else:
                try:
                    parse_date(show_date)
                except ValueError:
                    flash("Datum muss im Format YYYY-MM-DD sein.", "error")
                else:
                    db.execute(
                        """
                        UPDATE shows
                        SET title = ?, city = ?, venue = ?, show_date = ?, ticket_url = ?, notes = ?, updated_at = CURRENT_TIMESTAMP
                        WHERE id = ?
                        """,
                        (
                            title,
                            city,
                            venue,
                            show_date,
                            ticket_url or None,
                            notes or None,
                            show_id,
                        ),
                    )
                    db.commit()
                    flash("Show aktualisiert.", "success")
                    return redirect(url_for("admin_shows"))

        elif action == "delete":
            show_id = request.form.get("show_id", "").strip()
            if show_id:
                db.execute("DELETE FROM shows WHERE id = ?", (show_id,))
                db.commit()
                flash("Show gelöscht.", "success")
                return redirect(url_for("admin_shows"))

    shows = db.execute(
        """
        SELECT id, title, city, venue, show_date, ticket_url, notes
        FROM shows
        ORDER BY show_date ASC
        """
    ).fetchall()

    return render_template("admin_shows.html", shows=shows)


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
