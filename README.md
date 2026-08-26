# pirddiiqlab

This repository contains code and experiments for the pirddiiqlab project.

## Backend: Version 0 (pirddiiqlab-backend-v0)

This release adds a minimal Flask + SQLite backend (version 0) to serve as the default backend for the pirddiiqlab frontend (hosted on Replit).

Files added/updated in this release:

- `app.py` — minimal Flask backend implementing a version 0 API and an SQLite database (default file: `pirddiiqlab_v0.db`). See: https://github.com/make-DEEP-Human-Families-Healthy/pirddiiqlab/blob/main/app.py
- `RELEASE.md` — release notes for backend v0. See: https://github.com/make-DEEP-Human-Families-Healthy/pirddiiqlab/blob/main/RELEASE.md

Summary of backend v0 (quick reference)

- DB: SQLite file stored next to the app. Default path: `pirddiiqlab_v0.db`. Override with environment variable `PIRDDIIQLAB_DB_PATH`.
- Endpoints (app.py):
  - GET/POST /items — list items or create/update by key. POST JSON: {"key":"mykey","value":"some value"}.
  - GET/PUT/DELETE /items/<id> — operate on a specific item id.
  - POST /update — webhook/update endpoint. Expected JSON: {"source":"...","type":"set"|"delete","key":"...","value":"..."}. Saves update events in the `updates` table and applies simple set/delete ops to `items`.
  - GET /health — health/status, reports version `pirddiiqlab-backend-v0`.
  - GET/POST /init-db — creates database tables if missing.

Running locally or on Replit

1. Ensure Python 3.9+ is available.
2. Install dependencies: `pip install -r requirements.txt` (create `requirements.txt` with Flask and Flask-SQLAlchemy).
3. Run: `python app.py` (the server will bind to PORT env var if set, default 8080).
4. Initialize DB (optional): POST to `/init-db` once after starting the server.

Notes and next steps

- This is an intentionally small v0 backend to get the frontend connected quickly. It is not production hardened (no auth, no migrations, no concurrency tuning).
- Recommended follow-ups: add CORS, add authentication, migrate to Postgres for scale, add tests and schema migrations (Flask-Migrate / Alembic).

