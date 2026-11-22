import io
import json
import os
from datetime import date
from decimal import Decimal

from flask import (
    Flask, abort, flash, jsonify, redirect,
    render_template, request, send_file, url_for
)
from flask_login import (
    LoginManager, UserMixin, current_user,
    login_required, login_user, logout_user
)
from flask_sqlalchemy import SQLAlchemy
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from sqlalchemy import func, or_
from werkzeug.security import check_password_hash, generate_password_hash


db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "login"


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, server_default=func.now(), nullable=False)

    clients = db.relationship(
        "Client", backref="owner", cascade="all, delete-orphan"
    )
    invoices = db.relationship(
        "Invoice", backref="owner", cascade="all, delete-orphan"
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Client(db.Model):
    __tablename__ = "clients"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255))
    created_at = db.Column(
        db.DateTime, server_default=func.now(), nullable=False
    )

    invoices = db.relationship(
        "Invoice", backref="client", cascade="all, delete-orphan"
    )


class Invoice(db.Model):
    __tablename__ = "invoices"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    client_id = db.Column(
        db.Integer,
        db.ForeignKey("clients.id", ondelete="CASCADE"),
        nullable=False
    )
    description = db.Column(db.String(255), nullable=False)
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="pending")
    due_date = db.Column(db.Date, nullable=False, default=date.today)
    created_at = db.Column(db.DateTime, server_default=func.now(), nullable=False)

    @property
    def is_overdue(self):
        return self.status != "paid" and self.due_date < date.today()


def create_app(test_config=None):
    app = Flask(__name__)

    app.config.update(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-change-me"),
        SQLALCHEMY_DATABASE_URI=os.environ.get(
            "DATABASE_URL", "sqlite:///tracker.db"
        ),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    with app.app_context():
        db.create_all()

    # ---------------- DASHBOARD ----------------

    @app.route("/")
    @login_required
    def dashboard():
        total = db.session.query(
            func.coalesce(func.sum(Invoice.amount), 0)
        ).filter_by(user_id=current_user.id).scalar()

        paid = db.session.query(
            func.coalesce(func.sum(Invoice.amount), 0)
        ).filter_by(
            user_id=current_user.id,
            status="paid"
        ).scalar()

        pending = db.session.query(
            func.coalesce(func.sum(Invoice.amount), 0)
        ).filter_by(
            user_id=current_user.id,
            status="pending"
        ).scalar()

        overdue = Invoice.query.filter(
            Invoice.user_id == current_user.id,
            Invoice.status != "paid",
            Invoice.due_date < date.today()
        ).count()

        client_count = Client.query.filter_by(
            user_id=current_user.id
        ).count()

        paid_invoices = Invoice.query.filter_by(
            user_id=current_user.id,
            status="paid"
        ).all()

        buckets = {}

        for inv in paid_invoices:
            key = inv.created_at.strftime("%Y-%m")
            buckets[key] = (
                buckets.get(key, Decimal("0")) + Decimal(inv.amount)
            )

        chart_labels = sorted(buckets)
        chart_values = [float(buckets[k]) for k in chart_labels]

        return render_template(
            "dashboard.html",
            total=total,
            paid=paid,
            pending=pending,
            overdue=overdue,
            client_count=client_count,
            chart_labels=json.dumps(chart_labels),
            chart_values=json.dumps(chart_values),
        )

    # ---------------- SIGNUP ----------------

    @app.route("/signup", methods=["GET", "POST"])
    def signup():
        if current_user.is_authenticated:
            return redirect(url_for("dashboard"))

        if request.method == "POST":
            name = request.form.get("name", "").strip()
            email = request.form.get("email", "").strip().lower()
            password = request.form.get("password", "")

            if not name or not email or len(password) < 8:
                flash(
                    "Name, email and a password of at least 8 characters are required.",
                    "danger"
                )
                return render_template("signup.html")

            if User.query.filter_by(email=email).first():
                flash(
                    "An account with this email already exists.",
                    "danger"
                )
                return render_template("signup.html")

            user = User(name=name, email=email)
            user.set_password(password)

            db.session.add(user)
            db.session.commit()

            login_user(user)
            flash("Account created successfully.", "success")

            return redirect(url_for("dashboard"))

        return render_template("signup.html")

    # ---------------- LOGIN ----------------

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for("dashboard"))

        if request.method == "POST":
            email = request.form.get("email", "").strip().lower()
            password = request.form.get("password", "")

            user = User.query.filter_by(email=email).first()

            if not user or not user.check_password(password):
                flash("Invalid email or password.", "danger")
                return render_template("login.html")

            login_user(user)
            return redirect(url_for("dashboard"))

        return render_template("login.html")

    # ---------------- LOGOUT ----------------

    @app.route("/logout", methods=["POST"])
    @login_required
    def logout():
        logout_user()
        return redirect(url_for("login"))

    # ---------------- CLIENTS ----------------

    @app.route("/clients", methods=["GET", "POST"])
    @login_required
    def clients():
        if request.method == "POST":
            name = request.form.get("name", "").strip()
            email = request.form.get("email", "").strip()

            if not name:
                flash("Client name is required.", "danger")
            else:
                db.session.add(
                    Client(
                        user_id=current_user.id,
                        name=name,
                        email=email
                    )
                )
                db.session.commit()
                flash("Client added.", "success")

            return redirect(url_for("clients"))

        q = request.args.get("q", "").strip()

        query = Client.query.filter_by(user_id=current_user.id)

        if q:
            query = query.filter(
                or_(
                    Client.name.ilike(f"%{q}%"),
                    Client.email.ilike(f"%{q}%")
                )
            )

        return render_template(
            "clients.html",
            clients=query.order_by(Client.name).all(),
            q=q
        )

    @app.route("/clients/<int:client_id>/delete", methods=["POST"])
    @login_required
    def delete_client(client_id):
        client = Client.query.filter_by(
            id=client_id,
            user_id=current_user.id
        ).first_or_404()

        db.session.delete(client)
        db.session.commit()

        flash("Client and their invoices deleted.", "info")
        return redirect(url_for("clients"))

    # ---------------- INVOICES ----------------

    @app.route("/invoices", methods=["GET", "POST"])
    @login_required
    def invoices():
        if request.method == "POST":
            client_id = request.form.get("client_id", type=int)
            description = request.form.get("description", "").strip()

            try:
                amount = Decimal(request.form.get("amount", "0"))
            except Exception:
                amount = Decimal("0")

            due_date_text = request.form.get("due_date", "")

            try:
                due_date = (
                    date.fromisoformat(due_date_text)
                    if due_date_text else date.today()
                )
            except ValueError:
                due_date = date.today()

            client = Client.query.filter_by(
                id=client_id,
                user_id=current_user.id
            ).first()

            if not client or not description or amount <= 0:
                flash(
                    "Select a client, add a description and a valid amount.",
                    "danger"
                )
            else:
                db.session.add(
                    Invoice(
                        user_id=current_user.id,
                        client_id=client.id,
                        description=description,
                        amount=amount,
                        due_date=due_date,
                        status="pending"
                    )
                )
                db.session.commit()
                flash("Invoice added.", "success")

            return redirect(url_for("invoices"))

        q = request.args.get("q", "").strip()
        status = request.args.get("status", "").strip().lower()
        overdue_only = request.args.get("overdue") == "1"

        query = Invoice.query.filter_by(user_id=current_user.id)

        if q:
            query = query.join(Client).filter(
                or_(
                    Invoice.description.ilike(f"%{q}%"),
                    Client.name.ilike(f"%{q}%")
                )
            )

        if status in {"pending", "paid"}:
            query = query.filter_by(status=status)

        if overdue_only:
            query = query.filter(
                Invoice.status != "paid",
                Invoice.due_date < date.today()
            )

        invoices_list = query.order_by(Invoice.id.desc()).all()

        return render_template(
            "invoices.html",
            invoices=invoices_list,
            clients=Client.query.filter_by(
                user_id=current_user.id
            ).order_by(Client.name).all(),
            q=q,
            status=status,
            overdue_only=overdue_only,
            today=date.today()
        )

    @app.route("/invoices/<int:invoice_id>/paid", methods=["POST"])
    @login_required
    def mark_paid(invoice_id):
        invoice = Invoice.query.filter_by(
            id=invoice_id,
            user_id=current_user.id
        ).first_or_404()

        invoice.status = "paid"
        db.session.commit()

        flash("Invoice marked as paid.", "success")
        return redirect(url_for("invoices"))

    @app.route("/invoices/<int:invoice_id>/delete", methods=["POST"])
    @login_required
    def delete_invoice(invoice_id):
        invoice = Invoice.query.filter_by(
            id=invoice_id,
            user_id=current_user.id
        ).first_or_404()

        db.session.delete(invoice)
        db.session.commit()

        flash("Invoice deleted.", "info")
        return redirect(url_for("invoices"))

    # ---------------- INVOICE PDF ----------------

    @app.route("/invoices/<int:invoice_id>/pdf")
    @login_required
    def invoice_pdf(invoice_id):
        invoice = Invoice.query.filter_by(
            id=invoice_id,
            user_id=current_user.id
        ).first_or_404()

        buffer = io.BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4

        pdf.setFont("Helvetica-Bold", 20)
        pdf.drawString(25 * mm, height - 30 * mm, "Invoice")

        pdf.setFont("Helvetica", 11)
        pdf.drawString(
            25 * mm, height - 42 * mm,
            f"Invoice #{invoice.id}"
        )

        invoice_date = invoice.created_at

        if hasattr(invoice_date, "date"):
            invoice_date = invoice_date.date()

        pdf.drawString(
            25 * mm,
            height - 50 * mm,
            f"Date: {invoice_date or date.today()}"
        )
        pdf.drawString(
            25 * mm, height - 58 * mm,
            f"Due: {invoice.due_date}"
        )

        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(25 * mm, height - 78 * mm, "Bill To")

        pdf.setFont("Helvetica", 11)
        pdf.drawString(
            25 * mm, height - 87 * mm,
            invoice.client.name
        )

        if invoice.client.email:
            pdf.drawString(
                25 * mm, height - 95 * mm,
                invoice.client.email
            )

        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(25 * mm, height - 120 * mm, "Description")
        pdf.drawString(125 * mm, height - 120 * mm, "Amount")

        pdf.setFont("Helvetica", 11)
        pdf.drawString(
            25 * mm, height - 130 * mm,
            invoice.description
        )
        pdf.drawRightString(
            175 * mm, height - 130 * mm,
            f"${invoice.amount:,.2f}"
        )

        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(
            25 * mm, height - 155 * mm,
            f"Status: {invoice.status.title()}"
        )

        if invoice.is_overdue:
            pdf.drawString(
                25 * mm, height - 165 * mm,
                "OVERDUE"
            )

        pdf.showPage()
        pdf.save()
        buffer.seek(0)

        return send_file(
            buffer,
            mimetype="application/pdf",
            as_attachment=True,
            download_name=f"invoice-{invoice.id}.pdf"
        )

    # ---------------- MONTHLY EARNINGS API ----------------

    @app.route("/api/monthly-earnings")
    @login_required
    def monthly_earnings():
        paid_invoices = Invoice.query.filter_by(
            user_id=current_user.id,
            status="paid"
        ).all()

        buckets = {}

        for inv in paid_invoices:
            key = inv.created_at.strftime("%Y-%m")
            buckets[key] = (
                buckets.get(key, Decimal("0")) + Decimal(inv.amount)
            )

        labels = sorted(buckets)

        return jsonify({
            "labels": labels,
            "values": [float(buckets[k]) for k in labels]
        })

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)