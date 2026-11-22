# Freelancer Client & Invoice Tracker

A production-style Flask web application for managing clients and invoices. The project was upgraded beyond a simple CRUD/to-do app with authentication, per-user data isolation, invoice PDFs, analytics, overdue filtering, automated tests, and a deployable PostgreSQL configuration.

## Live demo

**https://invoice-tracker-srro.onrender.com**

> If the demo is sleeping on Render's free tier, the first request may take a little longer.

## Features

- User signup/login/logout
- Password hashing with Werkzeug
- Per-user client and invoice isolation
- Client search
- Invoice search and status filtering
- Overdue invoice detection
- Mark invoice as paid
- Invoice PDF download
- Dashboard KPI cards
- Monthly paid-earnings chart using Chart.js
- PostgreSQL/Supabase support
- SQLite support for local development/tests
- Pytest test suite
- Responsive UI
- Gunicorn deployment on Render

## Tech stack

- Python 3
- Flask
- Flask-Login
- Flask-SQLAlchemy
- PostgreSQL / Supabase
- SQLite for tests/local fallback
- ReportLab
- Chart.js
- Pytest
- Gunicorn
- Render

## Local setup

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:5000`.

## Environment variables

For production:

```text
DATABASE_URL=your_supabase_postgresql_url
SECRET_KEY=a-long-random-secret
```

Never commit database passwords or production secrets.

## Run tests

```bash
pytest -q
```

## Render configuration

Root Directory:

```text
invoice-tracker
```

Build Command:

```bash
pip install -r requirements.txt
```

Start Command:

```bash
gunicorn --bind 0.0.0.0:$PORT app:app
```

## Database migration

The current application uses SQLAlchemy models for `users`, `clients`, and `invoices`. Existing deployments that already have the old `clients`/`invoices` schema need a one-time database migration before the upgraded version is deployed.

If the old `tracker.db` contains real historical data, export/migrate it before deleting it. If it is only test/demo data, it can be skipped.

## Screenshots

Add these files before publishing the repository:

- `docs/screenshots/login.png`
- `docs/screenshots/dashboard.png`
- `docs/screenshots/invoices.png`
- `docs/screenshots/invoice-pdf.png`

Example Markdown:

```markdown
![Login](docs/screenshots/login.png)
![Dashboard](docs/screenshots/dashboard.png)
![Invoices](docs/screenshots/invoices.png)
```

## Project structure

```text
invoice-tracker/
├── app.py
├── requirements.txt
├── README.md
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── signup.html
│   ├── dashboard.html
│   ├── clients.html
│   └── invoices.html
├── static/
│   └── style.css
└── tests/
    ├── conftest.py
    ├── test_auth.py
    ├── test_isolation.py
    └── test_invoice.py
```

## Security notes

- Passwords are stored as hashes, not plaintext.
- Every client/invoice query is scoped to the authenticated user's ID.
- Invoice PDF routes also enforce ownership.
- Production `SECRET_KEY` should be a strong random value.
- Database credentials must stay in environment variables.
