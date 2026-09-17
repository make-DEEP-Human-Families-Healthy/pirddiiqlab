# pirddiiqlab

This repository contains code and experiments for the pirddiiqlab project: a Python health-data and insights platform for human families.

## Current status

The repository includes an early Flask backend prototype and standalone health-data experiments. The backend is currently suitable for local development and integration prototyping, but it is **not production-ready for medical or biological supply-chain data**.

The planned target is to evolve the backend into an API-first inventory and supply-chain service for the University of Illinois at Chicago Process Automation Virtual Lab System. The first production-oriented milestone is a test-only inventory workflow; live integration should wait until authentication, authorization, validation, auditing, migrations, and deployment controls are implemented.

## Backend: Version 0 (`pirddiiqlab-backend-v0`)

The current backend is a minimal Flask + SQLite service.

### Runtime implementations

- `app.py` — standalone Flask application and legacy v0 API.
- `pirddiiqlab/backend.py` — Flask application factory, SQLAlchemy models, and packaged API routes.
- `pirddiiqlab/cli.py` — command-line server launcher.
- `pirddiiqlab/init.py` — package metadata and `create_app` export.

The repository currently contains two similar backend entry points. They should be consolidated before production deployment so that the application, models, routes, and configuration have one source of truth.

### Current database

The prototype uses SQLite by default:

- Default database: `pirddiiqlab_v0.db`
- Override with `PIRDDIIQLAB_DB_PATH`
- Existing tables:
  - `items` — generic key-value records
  - `updates` — received update payloads and timestamps

SQLite is appropriate for local development and demonstrations. A server-based database such as PostgreSQL is recommended for concurrent production use.

### Current endpoints

- `GET/POST /items` — list items or create/update an item by key.
- `GET/PUT/DELETE /items/<id>` — operate on an individual item.
- `POST /update` — receive update events and optionally apply `set` or `delete` operations.
- `GET /health` — return backend health and version information.
- `GET/POST /init-db` — create missing prototype tables.

Example item payload:

```json
{"key": "mykey", "value": "some value"}
```

Example update payload:

```json
{"source": "frontend", "type": "set", "key": "mykey", "value": "some value"}
```

## Planned inventory and supply-chain architecture

The proposed inventory domain uses a normalized model:

```text
InventoryItem 1 ---- * InventoryLot 1 ---- * StockMovement
```

### Planned entities

- **`InventoryItem`** — catalog definition, including SKU, name, category, unit, reorder threshold, and active status.
- **`InventoryLot`** — a received batch, including lot number, quantity on hand, expiration date, storage location, and quarantine status.
- **`StockMovement`** — an inventory ledger entry for receipt, issue, transfer, disposal, or adjustment.

The intended relationship is:

- One inventory item can have many lots.
- One lot can have many stock movements.
- Stock movements should be append-only and auditable.
- Clients should not directly update `quantity_on_hand`; inventory changes should go through a transactional service operation.

### Planned API boundary

The future versioned API should use routes such as:

- `GET /api/v1/inventory`
- `POST /api/v1/inventory/receipts`
- `POST /api/v1/inventory/movements`
- `GET /api/v1/inventory/low-stock`
- `GET /api/v1/suppliers`
- `POST /api/v1/purchase-requests`
- `POST /api/v1/integrations/uic/events`
- `GET /health`

The UIC virtual lab should remain the user-facing system, while this service should become the source of truth for inventory and procurement records. Integration should use HTTPS, authenticated service credentials or OAuth/OIDC, request validation, idempotency keys, and audit logging.

### Migration plan

The inventory models and migrations are an architecture plan and are not yet installed in the repository. The repository currently has no Flask-Migrate/Alembic migration directory.

The planned migration structure is:

```text
migrations/
  versions/
    <revision>_create_inventory_tables.py
pirddiiqlab/
  models/
    __init__.py
    inventory.py
```

The planned migration tooling is Flask-Migrate/Alembic. Production schema changes should be applied through migrations rather than `db.create_all()`.

Before implementing the inventory schema, the project should:

1. Add and register `InventoryItem`, `InventoryLot`, and `StockMovement` models.
2. Add Flask-Migrate and create the initial inventory migration.
3. Consolidate `app.py` and `pirddiiqlab/backend.py`.
4. Add service-layer transactions for receiving, issuing, transferring, and disposing stock.
5. Add authentication, authorization, validation, structured logging, and audit controls.
6. Add tests for migration upgrades, stock movements, insufficient stock, expiry, quarantine, and immutable movement history.
7. Move deployed environments from SQLite to PostgreSQL.

## Research and analysis scripts

The repository also contains standalone scripts and experiments, including:

- Cohort sampling with `Cohort.py`
- Chicago dietary analysis with `DartUPirddiiq.py`
- Diabetes emergency-visit analysis with `DiabetesEDVisits.py`
- BMI calculators in `bmi.py`, `bmi2.py`, and `bmi3.py`
- Food-label processing with `FoodLabel.py`
- Meal-planning experiments in `MealPrep*.py`
- Diabetes machine-learning experimentation with `MinoritiesDiabetesBaselineML.py`
- Synthetic persona generation with `SyntheticFacebook.py`
- Medication/adherence concepts in `SodiumButyrate*.py`

These scripts currently operate independently on local files or sample data. They are not part of the Flask request path and should remain isolated from supply-chain operations until their inputs, outputs, validation, privacy, and testing are defined.

## Security note

Do not place credentials, tokens, or other secrets in source control. Any credential previously committed in `Bard.py` should be considered compromised: revoke it, rotate it, and replace it with an environment variable or managed secret. The current v0 API has no authentication or authorization and must not accept untrusted production traffic.

## Running locally

Python 3.9 or newer is required.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

The server listens on the `PORT` environment variable when set, or port `8080` by default.

The packaged CLI is intended to run as follows:

```bash
pip install -e .
pirddiiqlab-server --port 8080
```

The package layout and CLI should be tested and corrected before relying on the packaged command in deployment.

## Development dependencies

The `pyproject.toml` file defines optional development dependencies for pytest, coverage, Black, Flake8, and mypy:

```bash
pip install -e ".[dev]"
```

The repository should add a test suite before the backend is connected to the UIC virtual lab.

## License

See the repository license file for licensing terms.
