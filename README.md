# Happy Travels - Smart Bus Booking Platform

Production-ready Django + MySQL bus booking and management system for Tamil Nadu statewide routes.

## Highlights

- Passenger registration, login, profile, route search, seat selection, booking history, cancellation, PDF-style ticket page, QR ticket payload
- Operator/admin dashboards for buses, routes, drivers, conductors, bookings, revenue, occupancy, route performance, complaints, notifications
- Tamil Nadu seeded coverage: all 38 districts, major tourist towns, popular state routes, and common bus categories
- Responsive premium UI inspired by RedBus, AbhiBus, and MakeMyTrip, with dark mode and interactive transitions
- Live seat availability, dynamic fare calculation, route suggestions, demo tracking, REST JSON endpoints, secure session settings

## Tech Stack

- Frontend: HTML5, CSS3, JavaScript, Bootstrap 5
- Backend: Python, Django
- Database: MySQL

## Setup

```bash
cd outputs/tamilnadu-travels
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python manage.py seed_tn
python manage.py createsuperuser
python manage.py runserver
```

Update `.env` with your MySQL credentials before migration.

## MySQL Database

```sql
CREATE DATABASE tamilnadu_travels CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'tntravels_user'@'localhost' IDENTIFIED BY 'change-me';
GRANT ALL PRIVILEGES ON tamilnadu_travels.* TO 'tntravels_user'@'localhost';
FLUSH PRIVILEGES;
```

## Useful URLs

- `/` Home and bus search
- `/routes/` route discovery
- `/bookings/` passenger booking history
- `/dashboard/` admin analytics dashboard
- `/management/` admin modules and submodules
- `/notifications/` travel notifications
- `/complaints/` customer complaint management
- `/api/routes/` route API
- `/api/buses/?source=Chennai&destination=Madurai&date=2026-07-01` search API
- `/api/dashboard/` admin dashboard API

## Local Demo

For quick preview without MySQL, this project includes a local `.env` configured with SQLite. The seeded demo database supports:

- Admin login: `admin` / `admin12345`
- Passenger login: `demo` / `demo12345`

Start the server:

```bash
C:\Users\njeev\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe manage.py runserver 127.0.0.1:8000
```

Then open `http://127.0.0.1:8000/`.

## Portfolio Notes

This project is intentionally interview-friendly: it uses normalized models, clear services, seed data, secure configuration, reusable templates, and realistic business flows while staying simple enough to explain in a placement or internship demo.
