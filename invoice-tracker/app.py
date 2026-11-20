"""Freelancer Client & Invoice Tracker - Step 1 (clients + invoices, no login yet)."""
import sqlite3
from flask import Flask, g, redirect, render_template, request, url_for, flash

app = Flask(__name__)
app.config["SECRET_KEY"] = "change-this-before-deploying"
DATABASE = "tracker.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS clients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT
);
CREATE TABLE IF NOT EXISTS invoices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id INTEGER NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    description TEXT NOT NULL,
    amount REAL NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    created_at TEXT NOT NULL DEFAULT CURRENT_DATE
);
"""


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


@app.teardown_appcontext
def close_db(exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    with sqlite3.connect(DATABASE) as db:
        db.executescript(SCHEMA)


@app.route("/")
def dashboard():
    db = get_db()
    totals = db.execute(
        """SELECT
               COALESCE(SUM(amount), 0) AS invoiced,
               COALESCE(SUM(CASE WHEN status = 'paid' THEN amount END), 0) AS paid,
               COALESCE(SUM(CASE WHEN status = 'pending' THEN amount END), 0) AS pending
           FROM invoices"""
    ).fetchone()
    client_count = db.execute("SELECT COUNT(*) FROM clients").fetchone()[0]
    return render_template("dashboard.html", totals=totals, client_count=client_count)


@app.route("/clients", methods=["GET", "POST"])
def clients():
    db = get_db()
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        if not name:
            flash("Client name is required.", "danger")
        else:
            db.execute("INSERT INTO clients (name, email) VALUES (?, ?)", (name, email))
            db.commit()
            flash(f"Client '{name}' added.", "success")
        return redirect(url_for("clients"))
    rows = db.execute("SELECT * FROM clients ORDER BY name").fetchall()
    return render_template("clients.html", clients=rows)


@app.route("/clients/<int:client_id>/delete", methods=["POST"])
def delete_client(client_id):
    db = get_db()
    db.execute("DELETE FROM clients WHERE id = ?", (client_id,))
    db.commit()
    flash("Client deleted (their invoices too).", "info")
    return redirect(url_for("clients"))


@app.route("/invoices", methods=["GET", "POST"])
def invoices():
    db = get_db()
    if request.method == "POST":
        description = request.form.get("description", "").strip()
        client_id = request.form.get("client_id", type=int)
        try:
            amount = float(request.form.get("amount", ""))
        except ValueError:
            amount = None
        if not description or not client_id or amount is None or amount <= 0:
            flash("Pick a client, add a description and an amount above 0.", "danger")
        else:
            db.execute(
                "INSERT INTO invoices (client_id, description, amount) VALUES (?, ?, ?)",
                (client_id, description, amount),
            )
            db.commit()
            flash("Invoice added.", "success")
        return redirect(url_for("invoices"))
    rows = db.execute(
        """SELECT invoices.*, clients.name AS client_name
           FROM invoices JOIN clients ON clients.id = invoices.client_id
           ORDER BY invoices.id DESC"""
    ).fetchall()
    client_rows = db.execute("SELECT id, name FROM clients ORDER BY name").fetchall()
    return render_template("invoices.html", invoices=rows, clients=client_rows)


@app.route("/invoices/<int:invoice_id>/paid", methods=["POST"])
def mark_paid(invoice_id):
    db = get_db()
    db.execute("UPDATE invoices SET status = 'paid' WHERE id = ?", (invoice_id,))
    db.commit()
    return redirect(url_for("invoices"))


@app.route("/invoices/<int:invoice_id>/delete", methods=["POST"])
def delete_invoice(invoice_id):
    db = get_db()
    db.execute("DELETE FROM invoices WHERE id = ?", (invoice_id,))
    db.commit()
    return redirect(url_for("invoices"))


init_db()

if __name__ == "__main__":
    app.run(debug=True)
