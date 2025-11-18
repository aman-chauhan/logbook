"""Pytest configuration and shared fixtures for Logbook API tests.

This module provides common fixtures used across all test modules:
- app: Flask application configured for testing
- client: Flask test client
- db: Database instance
- sample_scribe: Pre-created test scribe
"""

import os
import pytest
from apiserver.run import create_app
from apiserver.extensions import db as _db
from apiserver.models import Scribe, Entry


@pytest.fixture(scope="function")
def app():
    """Create and configure a Flask application instance for testing.

    This fixture creates a fresh application instance for each test with:
    - In-memory SQLite database
    - Testing mode enabled
    - Fresh database tables

    Yields:
        Flask: Configured Flask application instance
    """
    # Set testing environment variable
    os.environ["TESTING"] = "true"

    # Create app with testing config
    app = create_app()

    # Establish application context
    with app.app_context():
        # Create all database tables
        _db.create_all()

        yield app

        # Clean up: drop all tables
        _db.session.remove()
        _db.drop_all()

    # Clean up environment
    os.environ.pop("TESTING", None)


@pytest.fixture(scope="function")
def client(app):
    """Create a Flask test client.

    Args:
        app: Flask application instance from app fixture

    Returns:
        FlaskClient: Test client for making requests
    """
    return app.test_client()


@pytest.fixture(scope="function")
def db(app):
    """Provide database instance with application context.

    Args:
        app: Flask application instance from app fixture

    Returns:
        SQLAlchemy: Database instance
    """
    with app.app_context():
        yield _db


@pytest.fixture(scope="function")
def sample_scribe(db):
    """Create a sample scribe for testing.

    Creates a scribe with known credentials:
    - Username: testuser
    - Email: test@example.com
    - Password: testpass123

    Args:
        db: Database instance from db fixture

    Returns:
        Scribe: Created scribe instance
    """
    scribe = Scribe(username="testuser", email="test@example.com")
    scribe.set_password("testpass123")
    db.session.add(scribe)
    db.session.commit()
    return scribe


@pytest.fixture(scope="function")
def sample_entry(db, sample_scribe):
    """Create a sample entry for testing.

    Creates a public entry belonging to sample_scribe.

    Args:
        db: Database instance from db fixture
        sample_scribe: Scribe instance from sample_scribe fixture

    Returns:
        Entry: Created entry instance
    """
    entry = Entry(
        content="This is a test entry",
        scribe_id=sample_scribe.id,
        visibility="public"
    )
    db.session.add(entry)
    db.session.commit()
    return entry


@pytest.fixture(scope="function")
def auth_headers(sample_scribe):
    """Create HTTP Basic Auth headers for sample_scribe.

    Args:
        sample_scribe: Scribe instance from sample_scribe fixture

    Returns:
        dict: Headers dictionary with Authorization header
    """
    import base64
    credentials = base64.b64encode(b"testuser:testpass123").decode("utf-8")
    return {"Authorization": f"Basic {credentials}"}
