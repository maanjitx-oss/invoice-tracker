# Freelancer Client & Invoice Tracker

A small web app for freelancers to track clients, invoices and payments.
Built with Python, Flask and SQLite.

## Features (so far)
- Add and delete clients
- Create invoices for a client, mark them paid
- Dashboard with total invoiced, paid and pending amounts

## Run it
```bash
python -m venv venv
venv\Scripts\activate        # Windows  (Mac/Linux: source venv/bin/activate)
pip install -r requirements.txt
python app.py
```
Open http://127.0.0.1:5000

## Planned
- Login / signup
- Invoice PDF download
- Charts on the dashboard
- Deploy online
