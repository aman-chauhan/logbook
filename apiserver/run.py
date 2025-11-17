"""
Application entry point.

This module creates the Flask application and runs it.
Used by the Flask CLI and Honcho.
"""

import os
from flask import Flask
from .extensions import db, migrate


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)

    # Load configuration directly from environment variables
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key-change-me")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "SQLALCHEMY_DATABASE_URI", "sqlite:///logbook.db"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JSON_SORT_KEYS"] = False

    # Testing mode uses in-memory database
    if os.getenv("TESTING") == "true":
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        app.config["TESTING"] = True

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Import models so Flask-Migrate can detect them
    from . import models  # noqa: F401

    # Register API blueprint
    from .api import api_bp

    app.register_blueprint(api_bp, url_prefix="/api")

    # Register a simple root endpoint
    @app.route("/")
    def index():
        """Root endpoint that provides API information."""
        return {
            "data": {
                "type": "api-info",
                "id": "1",
                "attributes": {
                    "message": "Logbook API",
                    "version": "1.0.0",
                    "endpoints": "/api",
                },
            }
        }

    # Register health check endpoint
    @app.route("/health")
    def health():
        """Health check endpoint for monitoring."""
        return {
            "data": {
                "type": "health-status",
                "id": "1",
                "attributes": {"status": "healthy"},
            }
        }

    return app


app = create_app()


@app.shell_context_processor
def make_shell_context():
    """
    Add database instance and models to Flask shell context.

    This makes these objects available in the Flask shell without
    needing to import them manually.

    Usage:
        $ flask shell
        >>> db
        <SQLAlchemy engine=sqlite:///...>
        >>> Scribe.query.all()
        [<Scribe john>, <Scribe jane>]
    """
    from .models import Scribe, Entry

    return {"db": db, "Scribe": Scribe, "Entry": Entry}


if __name__ == "__main__":
    app.run()
