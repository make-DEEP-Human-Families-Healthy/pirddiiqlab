"""
pirddiiqlab CLI: Command-line interface for running the backend server
"""

import argparse
import os
from .backend import create_app


def main():
    parser = argparse.ArgumentParser(description="pirddiiqlab: Health data and insights platform")
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.environ.get("PORT", 8080)),
        help="Port to bind to (default: 8080 or PORT env var)",
    )
    parser.add_argument(
        "--host",
        default=os.environ.get("HOST", "0.0.0.0"),
        help="Host to bind to (default: 0.0.0.0 or HOST env var)",
    )
    parser.add_argument(
        "--db-path",
        default=os.environ.get("PIRDDIIQLAB_DB_PATH", "pirddiiqlab_v0.db"),
        help="Path to SQLite database (default: pirddiiqlab_v0.db or PIRDDIIQLAB_DB_PATH env var)",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode",
    )

    args = parser.parse_args()
    app = create_app(db_path=args.db_path)
    app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
    main()
