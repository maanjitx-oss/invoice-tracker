Freelancer Client & Invoice Tracker

A full-stack, production-style web application built with Python and Flask to help freelancers manage clients, track invoices, monitor payments, and analyze monthly earnings.

The application includes secure authentication, user-level data isolation, invoice PDF generation, dashboard analytics, advanced filtering, and PostgreSQL database integration.

Live Demo: https://invoice-tracker-srro.onrender.com

---

Key Features

Authentication & Security

- User registration and login/logout
- Secure password hashing using Werkzeug
- User-specific data isolation
- Protected routes using Flask-Login
- Ownership validation for invoices and clients

Client Management

- Create and manage clients
- Client search functionality
- User-specific client records

Invoice Management

- Create and manage invoices
- Track pending and paid invoices
- Mark invoices as paid
- Search invoices by client name or description
- Filter invoices by payment status
- Identify overdue invoices
- Download invoices as PDF files

Dashboard & Analytics

- Dashboard KPI cards
- Monthly paid-earnings visualization
- Interactive charts using Chart.js
- Invoice and client statistics

Database & Deployment

- PostgreSQL database support through Supabase
- SQLite support for local development and testing
- Gunicorn application server
- Deployment on Render

---

Technology Stack

Category| Technologies
Backend| Python, Flask
Authentication| Flask-Login, Werkzeug
Database ORM| Flask-SQLAlchemy
Database| PostgreSQL, Supabase, SQLite
PDF Generation| ReportLab
Charts| Chart.js
Testing| Pytest
Deployment| Render, Gunicorn
Frontend| HTML, CSS, JavaScript

---

Application Screenshots

Screenshots will be added here.

Suggested screenshots:

- Login and Signup
- Dashboard and Monthly Earnings Chart
- Client Management
- Invoice Management and Filters
- Downloaded Invoice PDF

---

Project Structure

invoice-tracker/
│
├── app.py
├── requirements.txt
├── README.md
│
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── signup.html
│   ├── dashboard.html
│   ├── clients.html
│   └── invoices.html
│
├── static/
│   └── style.css
│
└── tests/
    ├── conftest.py
    ├── test_auth.py
    ├── test_isolation.py
    └── test_invoice.py

---

Run Locally

1. Clone the repository

git clone https://github.com/maanjitx-oss/invoice-tracker.git
cd invoice-tracker/invoice-tracker

2. Create a virtual environment

python -m venv .venv

3. Activate the environment

Windows:

.venv\Scripts\activate

macOS/Linux:

source .venv/bin/activate

4. Install dependencies

pip install -r requirements.txt

5. Start the application

python app.py

Open:

http://127.0.0.1:5000

---

Environment Variables

Configure the following environment variables for production:

DATABASE_URL=your_postgresql_database_url
SECRET_KEY=your_strong_random_secret

Security: Never commit database credentials, passwords, or production secrets to GitHub.

---

Automated Testing

The project includes automated tests covering authentication, user data isolation, and invoice functionality.

Run the test suite:

python -m pytest -q

Latest local test result: 5 passed

---

Production Deployment

The application is deployed using Render with Supabase PostgreSQL.

Render configuration:

Root Directory

invoice-tracker

Build Command

pip install -r requirements.txt

Start Command

gunicorn --bind 0.0.0.0:$PORT app:app

Live Application: https://invoice-tracker-srro.onrender.com

---

Security Considerations

- Passwords are stored using secure password hashing.
- Authenticated users can access only their own client and invoice records.
- Invoice PDF downloads enforce ownership checks.
- Production secrets are configured through environment variables.
- Database access is handled through SQLAlchemy.

---

Future Improvements

- Email notifications for overdue invoices
- Recurring invoice generation
- CSV and Excel report exports
- More advanced analytics
- Automated database migrations
- Role-based access control

---

Author

Developed as a full-stack Python web application project.

GitHub Repository: https://github.com/maanjitx-oss/invoice-tracker

Live Demo: https://invoice-tracker-srro.onrender.com