# Vehicle Parking Management System

A full-stack, multi-user parking-management application. An administrator manages parking lots and their individual spots, while users book, occupy, and release those spots in real time. The system tracks occupancy live, calculates parking cost automatically on release, shows analytics dashboards to the admin, and sends scheduled and on-demand email reports.

The frontend is a Vue 3 single-page application. The backend is a Flask REST API backed by SQLite, with Redis for caching and a Celery worker and scheduler handling background jobs such as reminders, monthly reports, and CSV exports.

## Features

### Authentication and authorization
- Token-based authentication using Flask-Security-Too. The client sends the token in an `Authentication-Token` header on every protected request.
- Role-based access control with two roles, `admin` and `user`, which are seeded automatically on first run.
- Passwords are hashed, and each user has its own auth token.

### Admin
- Create, edit, and delete parking lots. Creating a lot automatically generates its parking spots. Editing the spot count adds new spots or removes only currently-available ones, so occupied spots are never deleted from under a user.
- A lot cannot be deleted while any of its spots are still occupied.
- Search lots by ID, name, or location (case-insensitive).
- Summary dashboard with total lots, total spots, and occupied versus available counts, visualized with Chart.js.
- List all registered users.
- View the full reservation history across every lot.

### User
- Browse all lots with real-time availability.
- Book the first available spot in a lot; the spot is immediately marked occupied.
- Release a spot, at which point the system computes duration and cost as `duration_hours × lot_price`.
- View personal parking history with per-session cost and status.
- Export personal history to CSV, which is generated in the background and emailed, so the interface never blocks.

### Background jobs (Celery + Redis)
- Daily reminders at 6:00 PM to users who have not booked a spot that day.
- Monthly activity report on the 1st of each month at 9:00 AM: an HTML email with a usage table and the most-used lot, plus a CSV attachment.
- On-demand CSV export triggered from the interface, generated asynchronously and emailed.

### Performance
- Redis caching on read-heavy endpoints (summary, user list, available lots), each with a timeout tuned to how quickly its data changes.

## Architecture

```
Vue 3 SPA (Vite)                      Flask REST API
  - Vue Router                          - Flask-RESTful resources
  - Pinia (state)          HTTP/JSON    - Flask-Security-Too (token + RBAC)
  - Chart.js (analytics)  ----------->  - SQLAlchemy ORM
  - token in localStorage               - Flask-CORS
                                              |
              +-------------------------------+-------------------------------+
              |                               |                               |
         SQLite (ORM)                   Redis                            Celery
     User / Role / Lot /          cache + broker +                  worker + beat
     Spot / Reservation           result backend                 reminders, reports,
                                                                    CSV exports
                                                                         |
                                                                   SMTP (MailHog)
```

### Data model
| Entity | Key fields | Relationships |
|--------|-----------|---------------|
| User | email, password, full_name, roles | Role (many-to-many), Reservation (one-to-many) |
| Role | name, description | admin / user |
| Lot | name, location, address, pin_code, price, total_spots | Spot (one-to-many, cascade) |
| Spot | status (`A` available / `O` occupied), lot_id | Reservation (one-to-many) |
| Reservation | parking_start_time, parking_leaving_time, cost | User, Spot |

## Tech stack

| Layer | Technologies |
|-------|-------------|
| Frontend | Vue 3, Vite, Vue Router, Pinia, Chart.js |
| Backend | Python, Flask, Flask-RESTful, Flask-Security-Too, Flask-SQLAlchemy, Flask-Caching, Flask-CORS |
| Database | SQLite via SQLAlchemy ORM |
| Async and cache | Celery (worker + beat), Redis |
| Email | SMTP (MailHog for local development), Jinja2 HTML templates |

## Getting started

### Prerequisites
- Python 3.10 or newer
- Node.js 18 or newer with npm
- A running Redis server
- Optional: MailHog to capture development emails on `localhost:1025`

### 1. Backend
```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install flask flask-restful flask-security-too flask-sqlalchemy \
            flask-caching flask-cors celery redis jinja2

python app.py                   # API runs on http://localhost:5000
```
On first launch the database is created and an admin account is seeded:
- Email: `admin@parking`
- Password: `admin123`

Change these before deploying anywhere real.

### 2. Celery (background jobs)
Run each command in its own terminal, with Redis running:
```bash
# Worker
celery -A backend.celery_app.celery worker --loglevel=info --pool=solo

# Beat scheduler (daily reminders and monthly reports)
celery -A backend.celery_app.celery beat --loglevel=info
```

### 3. Frontend
```bash
cd frontend
npm install
npm run dev                     # http://localhost:5173
```

## API reference

| Method | Endpoint | Role | Description |
|--------|----------|------|-------------|
| POST | `/api/auth/register` | public | Register a new user |
| POST | `/api/auth/login` | public | Log in, returns an auth token |
| POST | `/api/auth/logout` | auth | Log out |
| GET, POST | `/api/admin/lots` | admin | List lots, or create a lot (auto-creates spots) |
| GET, PUT, DELETE | `/api/admin/lots/<id>` | admin | Read, update, or delete a lot |
| GET | `/api/admin/search?q=` | admin | Search lots by id, name, or location |
| GET | `/api/admin/summary` | admin | Aggregate statistics (cached) |
| GET | `/api/admin/history` | admin | All reservations |
| GET | `/api/admin/users` | admin | List users (cached) |
| GET | `/api/user/lots` | user | Available lots (cached) |
| POST | `/api/user/book/<lot_id>` | user | Book the first available spot |
| POST | `/api/user/release/<reservation_id>` | user | Release a spot and compute cost |
| GET | `/api/user/history` | user | Personal reservation history |
| POST | `/api/user/export` | user | Trigger an async CSV export by email |

## Project structure
```
Parking/
├── app.py                     # Flask app, config, route registration, DB and admin seed
├── backend/
│   ├── models.py              # SQLAlchemy models: User, Role, Lot, Spot, Reservation
│   ├── api.py                 # Admin and user REST resources
│   ├── auth_api.py            # Register / Login / Logout
│   ├── celery_app.py          # Celery tasks and beat schedule
│   ├── cache.py               # Flask-Caching (Redis) instance
│   ├── mail.py                # SMTP helper
│   └── user_datastore.py      # Flask-Security user datastore
└── frontend/
    └── src/
        ├── components/        # Admin and user views (dashboards, search, summary, history)
        ├── router/            # Vue Router routes
        └── utils/api.js       # Authorized fetch wrapper (token injection)
```

## What this project covers
- Building a REST API with authentication, role-based access control, and a normalized relational schema.
- Asynchronous background processing with Celery and Redis for scheduled and on-demand jobs.
- A caching strategy for read-heavy endpoints.
- A reactive single-page application with client-side routing, centralized state, and data visualization.
- End-to-end ownership from data model to API to background jobs to email to frontend.

## Possible improvements
- Move configuration and secrets to environment variables and rotate the seeded admin credentials.
- Add payment integration and time-slot reservations.
- Containerize the stack with Docker Compose (API, Redis, worker, frontend).
- Add automated tests: pytest for the API and Vitest for components.
- Move from SQLite to PostgreSQL for concurrent writes at scale.

Personal academic project built to explore full-stack architecture with asynchronous processing and caching.
