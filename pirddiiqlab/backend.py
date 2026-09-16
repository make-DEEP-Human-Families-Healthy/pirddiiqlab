"""
pirddiiqlab Backend v0
Minimal Flask + SQLite backend implementing core CRUD and update operations.
"""

from flask import Flask, request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import json

db = SQLAlchemy()


class Item(db.Model):
    """Data item: key-value storage"""
    __tablename__ = "items"
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String, unique=True, nullable=False)
    value = db.Column(db.String, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class UpdateEvent(db.Model):
    """Audit log: tracks all update events received"""
    __tablename__ = "updates"
    id = db.Column(db.Integer, primary_key=True)
    source = db.Column(db.String, nullable=True)
    payload = db.Column(db.Text, nullable=True)
    received_at = db.Column(db.DateTime, default=datetime.utcnow)


def create_app(db_path=None):
    """
    Factory function to create and configure the Flask application.

    Args:
        db_path (str, optional): Path to SQLite database file.
                                 If None, uses environment variable PIRDDIIQLAB_DB_PATH
                                 or defaults to 'pirddiiqlab_v0.db'

    Returns:
        Flask: Configured Flask application instance
    """
    app = Flask(__name__)

    if db_path is None:
        db_path = os.environ.get("PIRDDIIQLAB_DB_PATH", "pirddiiqlab_v0.db")

    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    register_routes(app)

    with app.app_context():
        db.create_all()

    return app


def register_routes(app):
    """Register all API routes for the backend."""

    @app.route("/health", methods=["GET"])
    def health():
        return jsonify({"status": "ok", "version": "pirddiiqlab-backend-v0"})

    @app.route("/init-db", methods=["POST", "GET"])
    def init_db():
        db.create_all()
        db_path = app.config["SQLALCHEMY_DATABASE_URI"].replace("sqlite:///", "")
        return jsonify({"status": "ok", "db_path": db_path}), 201

    @app.route("/items", methods=["GET", "POST"])
    def items():
        if request.method == "GET":
            all_items = Item.query.all()
            return jsonify([
                {
                    "id": i.id,
                    "key": i.key,
                    "value": i.value,
                    "updated_at": i.updated_at.isoformat() if i.updated_at else None,
                }
                for i in all_items
            ])

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

        new_item = Item(key=key, value=value)
        db.session.add(new_item)
        db.session.commit()
        return jsonify({"status": "created", "id": new_item.id}), 201

    @app.route("/items/<int:item_id>", methods=["GET", "PUT", "DELETE"])
    def item_detail(item_id):
        item = Item.query.get_or_404(item_id)

        if request.method == "GET":
            return jsonify({
                "id": item.id,
                "key": item.key,
                "value": item.value,
                "updated_at": item.updated_at.isoformat() if item.updated_at else None,
            })

        if request.method == "PUT":
            data = request.get_json() or {}
            item.value = data.get("value", item.value)
            db.session.commit()
            return jsonify({"status": "updated"})

        db.session.delete(item)
        db.session.commit()
        return jsonify({"status": "deleted"})

    @app.route("/update", methods=["POST"])
    def on_update():
        data = request.get_json() or {}
        source = data.get("source", "unknown")

        payload_text = None
        try:
            payload_text = json.dumps(data)
        except Exception:
            payload_text = str(data)

        event = UpdateEvent(source=source, payload=payload_text)
        db.session.add(event)

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


def run_dev_server(host="0.0.0.0", port=8080, db_path=None):
    app = create_app(db_path=db_path)
    app.run(host=host, port=port, debug=True)
