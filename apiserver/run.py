"""
Application entry point.

This module creates the Flask application and runs it.
Used by the Flask CLI and Honcho.
"""

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()


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

    # Register a simple root endpoint
    @app.route("/")
    def index():
        """Root endpoint that provides API information."""
        return {
            "success": True,
            "data": {
                "message": "Logbook API",
                "version": "1.0.0",
                "endpoints": "/api",
            },
        }

    # Register health check endpoint
    @app.route("/health")
    def health():
        """Health check endpoint for monitoring."""
        return {"success": True, "data": {"status": "healthy"}}

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
        >>> User.query.all()
        [<Scribe john>, <Scribe jane>]
    """
    return {"db": db}


if __name__ == "__main__":
    app.run()
