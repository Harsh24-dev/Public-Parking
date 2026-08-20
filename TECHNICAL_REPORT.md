# Technical Report — Vehicle Parking Management System

**Author:** Harsh · **Type:** Full-stack web application · **Stack:** Flask · Vue 3 · Celery · Redis · SQLite

---

## 1. Problem Statement

Design a multi-user application that lets an administrator manage parking infrastructure (lots and individual spots) while end users reserve and release spots on demand. The system must track occupancy in real time, compute parking costs automatically, surface analytics to the admin, and keep users engaged through scheduled email communications — all without blocking the request/response cycle for slow work such as report generation.

---

## 2. High-Level Design

The application follows a **decoupled client–server architecture**:

- A **Vue 3 single-page application** renders all UI and holds no business logic beyond presentation and auth-token handling.
- A **Flask REST API** owns all business rules, persistence, and authorization.
- A **Celery worker + beat scheduler** executes asynchronous and time-triggered jobs out of band.
- **Redis** serves triple duty: response cache, Celery message broker, and Celery result backend.

This separation means the frontend and backend can be developed, deployed, and scaled independently, and the API is equally consumable by a future mobile client.

---

## 3. Data Model & Design Decisions

Five entities model the domain (see `backend/models.py`):

- **User / Role / user_roles** — a many-to-many role association enables RBAC. Flask-Security-Too adds `fs_uniquifier` and `fs_token_uniquifier` for stateless token auth.
- **Lot** — a physical parking location with a price and a spot count.
- **Spot** — belongs to a lot; a single-character `status` field (`A`/`O`) keeps occupancy checks index-friendly and cheap.
- **Reservation** — the transactional record linking a user to a spot, storing start/leave timestamps and computed cost.

**Key decisions:**

- **Spots are materialized rows, not a counter.** When a lot is created with *N* spots, *N* `Spot` rows are inserted. This lets each spot be independently reserved, released, and audited, and makes "which spots are free" a simple filtered query rather than derived arithmetic.
- **Cascade deletes** (`cascade="all, delete"`) keep the graph consistent — deleting a lot cleans up its spots and their reservations.
- **Cost is computed at release time**, not stored per hour: `cost = round(duration_hours × lot.price, 2)`, where duration is derived from the two timestamps. This keeps historical costs correct even if a lot's price later changes.

---

## 4. Authentication & Authorization

- Login verifies the password via `flask_security.utils.verify_password` and returns a per-user auth token.
- Every protected resource is decorated with `@auth_required("token")`; the client attaches the token in the `Authentication-Token` header (see `frontend/src/utils/api.js`).
- Admin-only endpoints call a small `is_admin()` guard (`current_user.has_role("admin")`) and return **403** on violation — authorization is enforced server-side on every request, never trusted to the UI.
- Roles and a default admin are **idempotently seeded** at startup using `find_or_create_role` / `find_user`, so the app is runnable immediately after clone.

---

## 5. Asynchronous Processing (Celery + Redis)

Slow or scheduled work is delegated to Celery so the API stays responsive:

| Task | Trigger | Behavior |
|------|---------|----------|
| `daily_reminders` | Beat, 18:00 daily | Emails users with no active reservation that day |
| `monthly_report` | Beat, 09:00 on the 1st | Builds a per-user HTML report (most-used lot, totals) via Jinja2 + a CSV attachment |
| `export_csv_for_user` | On-demand from UI | Generates the user's full history CSV and emails a download link |
| `generate_csv` | Chained | Writes the CSV file into `static/` for download |

**Design notes:**
- The CSV export endpoint returns **HTTP 202 Accepted** immediately and hands off to Celery via `.delay()` — a textbook non-blocking pattern.
- Beat schedules use `crontab()` expressions with the worker pinned to `Asia/Kolkata` for correct local-time delivery.
- Email is rendered as HTML with Jinja2 templates and sent through an SMTP relay (MailHog locally on port 1025), so the same code path works with a real SMTP provider in production.

---

## 6. Caching Strategy

Read-heavy, low-volatility endpoints are cached in Redis via Flask-Caching with **per-endpoint timeouts** tuned to how fast the underlying data changes:

- `admin/summary` → 30 s (aggregate stats)
- `admin/users` → 60 s (user list changes rarely)
- `user/lots` → 5 s (availability changes fast, so a short TTL balances freshness vs. load)

A namespaced key prefix (`vp2_`) isolates this app's keys in a shared Redis instance.

---

## 7. Notable Business Logic

- **Adaptive spot resizing:** editing a lot's `total_spots` diffs against the current count and adds new available spots or removes *only currently-available* ones — occupied spots are never destroyed out from under a user.
- **Safe lot deletion:** blocked with **400** if any spot is occupied.
- **Flexible search:** numeric queries resolve by lot ID; text queries do a case-insensitive `ILIKE` match on name/location — a single endpoint serving both intents.

---

## 8. Challenges & Solutions

| Challenge | Solution |
|-----------|----------|
| Keeping the UI responsive during report/CSV generation | Offloaded to Celery; endpoint returns `202` and emails the result |
| Cross-origin cookies/tokens between `:5173` and `:5000` | Configured Flask-CORS with `supports_credentials` and explicit origins |
| Stale vs. fresh reads under load | Per-endpoint Redis TTLs matched to data volatility |
| Correct historical costs when prices change | Compute and persist cost at release time from timestamps |
| Idempotent first-run setup | `find_or_create_role` / conditional admin seeding at startup |

---

## 9. Results

A fully functional two-persona application: admins manage lots/spots with live analytics and full history; users book and release spots with automatic billing, personal history, and self-service CSV export. Scheduled reminders and monthly reports run unattended via Celery beat.

---

## 10. Future Work

- Externalize configuration and secrets to environment variables; rotate seeded credentials.
- Introduce time-slot reservations and online payment.
- Add a comprehensive test suite (pytest for the API layer, Vitest for Vue components).
- Containerize the full stack (API + worker + beat + Redis + frontend) with Docker Compose.
- Swap SQLite for PostgreSQL for concurrent-write durability at scale.
