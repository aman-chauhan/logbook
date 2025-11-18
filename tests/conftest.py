"""Pytest configuration and shared fixtures for Logbook API tests.

This module provides common fixtures used across all test modules:
- app: Flask application configured for testing
- client: Flask test client
- db: Database instance with foreign key constraints enabled
- faker: Faker instance for generating realistic test data
- sample_scribe: Pre-created test scribe
"""

import os
import pytest
from faker import Faker
from sqlalchemy import event
from apiserver.run import create_app
from apiserver.extensions import db as _db
from apiserver.models import Scribe, Entry


@pytest.fixture(scope="function")
def app():
    """Create and configure a Flask application instance for testing.

    This fixture creates a fresh application instance for each test with:
    - In-memory SQLite database
    - Foreign key constraints enabled
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
        # Enable foreign key constraints for SQLite
        @event.listens_for(_db.engine, "connect")
        def set_sqlite_pragma(dbapi_conn, connection_record):
            cursor = dbapi_conn.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()
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

    Note:
        The app fixture already establishes the application context,
        so we just return the db instance directly.
    """
    return _db


@pytest.fixture(scope="function")
def faker():
    """Create a Faker instance for generating test data.

    Returns:
        Faker: Faker instance for generating realistic test data
    """
    return Faker()


@pytest.fixture(scope="function")
def sample_scribe(db, faker):
    """Create a sample scribe for testing using Faker.

    Creates a scribe with realistic fake data and known password.

    Args:
        db: Database instance from db fixture
        faker: Faker instance for generating data

    Returns:
        Scribe: Created scribe instance with password "testpass123"
    """
    scribe = Scribe(
        username=faker.user_name(),
        email=faker.email()
    )
    scribe.set_password("testpass123")
    db.session.add(scribe)
    db.session.commit()
    return scribe


@pytest.fixture(scope="function")
def sample_entry(db, sample_scribe, faker):
    """Create a sample entry for testing using Faker.

    Creates a public entry belonging to sample_scribe with realistic content.

    Args:
        db: Database instance from db fixture
        sample_scribe: Scribe instance from sample_scribe fixture
        faker: Faker instance for generating data

    Returns:
        Entry: Created entry instance
    """
    entry = Entry(
        content=faker.text(max_nb_chars=200),
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
    credentials = base64.b64encode(
        f"{sample_scribe.username}:testpass123".encode()
    ).decode("utf-8")
    return {"Authorization": f"Basic {credentials}"}


@pytest.fixture(scope="function")
def scribe_factory(db, faker):
    """Factory fixture for creating multiple scribes.

    Returns a function that creates a new scribe with realistic data.

    Args:
        db: Database instance from db fixture
        faker: Faker instance for generating data

    Returns:
        callable: Function that creates and returns a Scribe instance
    """
    def _create_scribe(username=None, email=None, password="testpass123", bio=None):
        scribe = Scribe(
            username=username or faker.user_name(),
            email=email or faker.email(),
            bio=bio or (faker.sentence() if faker.boolean() else None)
        )
        scribe.set_password(password)
        db.session.add(scribe)
        db.session.commit()
        return scribe
    return _create_scribe


@pytest.fixture(scope="function")
def entry_factory(db, faker):
    """Factory fixture for creating multiple entries.

    Returns a function that creates a new entry with realistic data.

    Args:
        db: Database instance from db fixture
        faker: Faker instance for generating data

    Returns:
        callable: Function that creates and returns an Entry instance
    """
    def _create_entry(scribe_id, content=None, visibility="public"):
        entry = Entry(
            content=content or faker.text(max_nb_chars=200),
            scribe_id=scribe_id,
            visibility=visibility
        )
        db.session.add(entry)
        db.session.commit()
        return entry
    return _create_entry
