from flask import Flask, request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
# Version 0 backend database: SQLite file (pirddiiqlab_v0.db) stored next to the app.
DB_PATH = os.environ.get("PIRDDIIQLAB_DB_PATH", "pirddiiqlab_v0.db")
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# Import models after db is created
class Item(db.Model):
    __tablename__ = "items"
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String, unique=True, nullable=False)
    value = db.Column(db.String, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class UpdateEvent(db.Model):
    __tablename__ = "updates"
    id = db.Column(db.Integer, primary_key=True)
    source = db.Column(db.String, nullable=True)
    payload = db.Column(db.Text, nullable=True)
    received_at = db.Column(db.DateTime, default=datetime.utcnow)


@app.route("/init-db", methods=["POST", "GET"])
def init_db():
    """Initialize the version 0 SQLite database and create tables."""
    db.create_all()
    return jsonify({"status": "ok", "db_path": DB_PATH}), 201


@app.route("/items", methods=["GET", "POST"])
def items():
    if request.method == "GET":
        all_items = Item.query.all()
        return jsonify([{"id": i.id, "key": i.key, "value": i.value, "updated_at": i.updated_at.isoformat() if i.updated_at else None} for i in all_items])
    data = request.get_json() or {}
    key = data.get("key")
    value = data.get("value")
    if not key:
        abort(400, description="'key' is required")
    existing = Item.query.filter_by(key=key).first()
    if existing:
        existing.value = value
        db.session.commit()
        return jsonify({"status": "updated", "id": existing.id})
    it = Item(key=key, value=value)
    db.session.add(it)
    db.session.commit()
    return jsonify({"status": "created", "id": it.id}), 201


@app.route("/items/<int:item_id>", methods=["GET", "PUT", "DELETE"])
def item_detail(item_id):
    it = Item.query.get_or_404(item_id)
    if request.method == "GET":
        return jsonify({"id": it.id, "key": it.key, "value": it.value, "updated_at": it.updated_at.isoformat() if it.updated_at else None})
    if request.method == "PUT":
        data = request.get_json() or {}
        it.value = data.get("value", it.value)
        db.session.commit()
        return jsonify({"status": "updated"})
    # DELETE
    db.session.delete(it)
    db.session.commit()
    return jsonify({"status": "deleted"})


@app.route("/update", methods=["POST"])
def on_update():
    """Endpoint to receive update events from the frontend (Replit) or from webhooks.
    Stores payload in the version 0 DB 'updates' table and optionally applies changes to items.
    Expected JSON: {"source": "replit"|"frontend"|..., "type": "set"|"delete", "key": "...", "value": "..."}
    """
    data = request.get_json() or {}
    source = data.get("source", "unknown")
    payload_text = None
    try:
        import json
        payload_text = json.dumps(data)
    except Exception:
        payload_text = str(data)
    ev = UpdateEvent(source=source, payload=payload_text)
    db.session.add(ev)

    # Optionally apply change to items for simple "set" updates
    op = data.get("type")
    if op == "set":
        key = data.get("key")
        value = data.get("value")
        if key:
            existing = Item.query.filter_by(key=key).first()
            if existing:
                existing.value = value
            else:
                db.session.add(Item(key=key, value=value))
    elif op == "delete":
        key = data.get("key")
        if key:
            existing = Item.query.filter_by(key=key).first()
            if existing:
                db.session.delete(existing)

    db.session.commit()

    return jsonify({"status": "received", "source": source, "applied_op": op}), 201


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "version": "pirddiiqlab-backend-v0"})


if __name__ == "__main__":
    # Ensure DB exists on startup in simple deployments like Replit
    with app.app_context():
        db.create_all()
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
