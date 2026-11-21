"""Freelancer Client & Invoice Tracker - Supabase PostgreSQL."""

import os
import psycopg2
from urllib.parse import urlparse, unquote
from psycopg2.extras import DictCursor
from flask import Flask, g, redirect, render_template, request, url_for, flash

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY",
    "change-this-secret"
)


class Database:
    def __init__(self, connection):
        self.connection = connection

    def execute(self, query, params=()):
        cursor = self.connection.cursor()
        cursor.execute(query.replace("?", "%s"), params)
        return cursor

    def commit(self):
        self.connection.commit()

    def close(self):
        self.connection.close()


def get_db():
    if "db" not in g:
        database_url = os.environ.get("DATABASE_URL")

        if not database_url:
            raise RuntimeError("DATABASE_URL is not configured")

        parsed = urlparse(database_url)

        connection = psycopg2.connect(
            host=parsed.hostname,
            port=parsed.port or 5432,
            user=parsed.username,
            password=unquote(parsed.password),
            dbname=parsed.path.lstrip("/"),
            sslmode="require",
            cursor_factory=DictCursor
        )

        g.db = Database(connection)

    return g.db


@app.teardown_appcontext
def close_db(exc):
    db = g.pop("db", None)

    if db is not None:
        db.close()


@app.route("/")
def dashboard():
    db = get_db()

    totals = db.execute(
        """
        SELECT
            COALESCE(SUM(amount), 0) AS invoiced,
            COALESCE(
                SUM(
                    CASE
                        WHEN status = 'paid' THEN amount
                        ELSE 0
                    END
                ),
                0
            ) AS paid,
            COALESCE(
                SUM(
                    CASE
                        WHEN status = 'pending' THEN amount
                        ELSE 0
                    END
                ),
                0
            ) AS pending
        FROM invoices
        """
    ).fetchone()

    client_count = db.execute(
        "SELECT COUNT(*) FROM clients"
    ).fetchone()[0]

    return render_template(
        "dashboard.html",
        totals=totals,
        client_count=client_count
    )


@app.route("/clients", methods=["GET", "POST"])
def clients():
    db = get_db()

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()

        if not name:
            flash("Client name is required.", "danger")
        else:
            db.execute(
                """
                INSERT INTO clients (name, email)
                VALUES (?, ?)
                """,
                (name, email)
            )

            db.commit()

            flash(
                f"Client '{name}' added.",
                "success"
            )

        return redirect(url_for("clients"))

    rows = db.execute(
        """
        SELECT *
        FROM clients
        ORDER BY name
        """
    ).fetchall()

    return render_template(
        "clients.html",
        clients=rows
    )


@app.route("/clients/<int:client_id>/delete", methods=["POST"])
def delete_client(client_id):
    db = get_db()

    db.execute(
        """
        DELETE FROM clients
        WHERE id = ?
        """,
        (client_id,)
    )

    db.commit()

    flash(
        "Client deleted (their invoices too).",
        "info"
    )

    return redirect(url_for("clients"))


@app.route("/invoices", methods=["GET", "POST"])
def invoices():
    db = get_db()

    if request.method == "POST":
        description = request.form.get(
            "description",
            ""
        ).strip()

        client_id = request.form.get(
            "client_id",
            type=int
        )

        try:
            amount = float(
                request.form.get("amount", "")
            )
        except ValueError:
            amount = None

        if (
            not description
            or not client_id
            or amount is None
            or amount <= 0
        ):
            flash(
                "Pick a client, add a description and an amount above 0.",
                "danger"
            )

        else:
            db.execute(
                """
                INSERT INTO invoices
                    (client_id, description, amount)
                VALUES (?, ?, ?)
                """,
                (
                    client_id,
                    description,
                    amount
                )
            )

            db.commit()

            flash(
                "Invoice added.",
                "success"
            )

        return redirect(url_for("invoices"))

    rows = db.execute(
        """
        SELECT
            invoices.*,
            clients.name AS client_name
        FROM invoices
        JOIN clients
            ON clients.id = invoices.client_id
        ORDER BY invoices.id DESC
        """
    ).fetchall()

    client_rows = db.execute(
        """
        SELECT id, name
        FROM clients
        ORDER BY name
        """
    ).fetchall()

    return render_template(
        "invoices.html",
        invoices=rows,
        clients=client_rows
    )


@app.route(
    "/invoices/<int:invoice_id>/paid",
    methods=["POST"]
)
def mark_paid(invoice_id):
    db = get_db()

    db.execute(
        """
        UPDATE invoices
        SET status = 'paid'
        WHERE id = ?
        """,
        (invoice_id,)
    )

    db.commit()

    return redirect(url_for("invoices"))


@app.route(
    "/invoices/<int:invoice_id>/delete",
    methods=["POST"]
)
def delete_invoice(invoice_id):
    db = get_db()

    db.execute(
        """
        DELETE FROM invoices
        WHERE id = ?
        """,
        (invoice_id,)
    )

    db.commit()

    return redirect(url_for("invoices"))


if __name__ == "__main__":
    app.run(debug=True)