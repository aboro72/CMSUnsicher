"""Intentionally vulnerable training CMS. Use only with fictional data."""
import os
import sqlite3
from pathlib import Path

from flask import Flask, abort, g, redirect, render_template, request, session, url_for

app = Flask(__name__)
app.config.update(SECRET_KEY="cmsunsicher-training-secret", SESSION_COOKIE_HTTPONLY=False)
DATABASE = Path(app.instance_path) / "cms.sqlite3"


def db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(error=None):
    connection = g.pop("db", None)
    if connection is not None:
        connection.close()


def init_db():
    DATABASE.parent.mkdir(parents=True, exist_ok=True)
    with app.app_context():
        db().executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT,
                role TEXT, email TEXT, note TEXT);
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY, title TEXT, body TEXT, author_id INTEGER);
        """)
        if db().execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0:
            db().executemany("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?)", [
                (1, "admin", "admin123", "admin", "admin@example.test", "Interne Demo-Notiz: FLAG{profile_idor}"),
                (2, "demo", "demo123", "user", "demo@example.test", "Nur fiktive Daten verwenden."),
            ])
            db().execute("INSERT INTO posts (title, body, author_id) VALUES (?, ?, ?)",
                         ("Willkommen im CMS Unsicher", "<p>Ein absichtlich verwundbares CMS für Sicherheitsübungen.</p>", 1))
        db().commit()


@app.before_request
def load_user():
    g.user = db().execute("SELECT * FROM users WHERE id = ?", (session.get("user_id"),)).fetchone()


@app.route("/")
def index():
    query = request.args.get("q", "")
    # Training vulnerability: SQL injection in search.
    posts = db().execute(f"SELECT posts.*, users.username FROM posts LEFT JOIN users ON users.id = posts.author_id WHERE title LIKE '%{query}%' ORDER BY posts.id DESC").fetchall()
    return render_template("index.html", posts=posts, query=query)


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        # Training vulnerability: SQL injection and plaintext passwords.
        user = db().execute(f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'").fetchone()
        if user:
            session["user_id"] = user["id"]
            return redirect(url_for("index"))
        error = "Anmeldung fehlgeschlagen."
    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.route("/posts/new", methods=["GET", "POST"])
def new_post():
    if not g.user:
        return redirect(url_for("login"))
    if request.method == "POST":
        # Deliberately no CSRF token; body is rendered as raw HTML.
        db().execute("INSERT INTO posts (title, body, author_id) VALUES (?, ?, ?)",
                     (request.form.get("title", ""), request.form.get("body", ""), g.user["id"]))
        db().commit()
        return redirect(url_for("index"))
    return render_template("new.html")


@app.route("/profile/<int:user_id>")
def profile(user_id):
    if not g.user:
        return redirect(url_for("login"))
    # Training vulnerability: any logged-in user can read another profile.
    user = db().execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    if not user:
        abort(404)
    return render_template("profile.html", user=user)


@app.route("/admin")
def admin():
    if not g.user:
        return redirect(url_for("login"))
    # Training vulnerability: missing role check.
    return render_template("admin.html", users=db().execute("SELECT * FROM users").fetchall())


@app.route("/admin/delete/<int:post_id>", methods=["GET", "POST"])
def delete_post(post_id):
    if not g.user:
        return redirect(url_for("login"))
    # Training vulnerability: destructive GET, missing role check and CSRF protection.
    db().execute("DELETE FROM posts WHERE id = ?", (post_id,))
    db().commit()
    return redirect(url_for("index"))


@app.route("/health")
def health():
    db().execute("SELECT 1")
    return {"status": "ok"}


if __name__ == "__main__":
    from waitress import serve
    init_db()
    serve(app, host=os.environ.get("CMS_HOST", "127.0.0.1"), port=int(os.environ.get("CMS_PORT", "8000")))
