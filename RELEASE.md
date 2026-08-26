# Release: pirddiiqlab-backend-v0
Date: 2026-08-26

Summary
-------
This release introduces the initial backend (version 0) for the pirddiiqlab frontend. It is a minimal Flask application backed by a local SQLite database and provides simple endpoints for storing items and recording update events.

Files added
- app.py — Flask application implementing the v0 API and SQLite persistence.

API (high-level)
- GET/POST /items — list or create/update items by key. Example POST payload: {"key":"alpha","value":"123"}.
- GET/PUT/DELETE /items/<id> — operate on single item records by id.
- POST /update — webhook/update endpoint. Saves each incoming payload to the `updates` table and applies simple set/delete operations to the `items` table when applicable. Expected JSON: {"source":"frontend","type":"set","key":"...","value":"..."}.
- GET /health — returns status and version label "pirddiiqlab-backend-v0".
- GET/POST /init-db — create database tables (safe to call once on start).

Deployment notes
- Default DB file: `pirddiiqlab_v0.db` in the application directory. Override with env var `PIRDDIIQLAB_DB_PATH`.
- Replit: add `app.py` and `requirements.txt`, set run command to `python app.py`. Replit will provide a PORT env var; the app listens on that automatically.
- CORS: If the frontend is served from a different origin, add Flask-CORS to allow browser requests.

Testing (examples)
- Create/update item:
  curl -X POST https://<repl-url>/items -H "Content-Type: application/json" -d '{"key":"alpha","value":"123"}'
- Send update event:
  curl -X POST https://<repl-url>/update -H "Content-Type: application/json" -d '{"source":"frontend","type":"set","key":"alpha","value":"456"}'
- Health check:
  curl https://<repl-url>/health

Known limitations & next steps
- No authentication/authorization included — do not accept untrusted inputs in production.
- No schema migrations included. For schema evolution add Flask-Migrate/Alembic.
- Consider moving to Postgres or another server-based DB when scaling.
- Add tests, logging, and request validation.
