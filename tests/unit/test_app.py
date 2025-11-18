"""Unit tests for application factory and configuration.

Tests for:
- create_app() factory function
- Application configuration
- Extension initialization
- Blueprint registration
- Root endpoints
"""

import pytest
import os
from apiserver.run import create_app
from apiserver.extensions import db, migrate


class TestApplicationFactory:
    """Test suite for create_app() factory function."""

    @pytest.mark.unit
    def test_create_app_returns_flask_app(self):
        """Test that create_app returns a Flask application instance."""
        app = create_app()
        assert app is not None
        assert app.__class__.__name__ == "Flask"

    @pytest.mark.unit
    def test_create_app_with_testing_config(self):
        """Test that TESTING environment variable enables test mode."""
        os.environ["TESTING"] = "true"
        app = create_app()

        assert app.config["TESTING"] is True
        assert app.config["SQLALCHEMY_DATABASE_URI"] == "sqlite:///:memory:"

        # Clean up
        os.environ.pop("TESTING")

    @pytest.mark.unit
    def test_create_app_default_config(self):
        """Test default configuration values."""
        # Ensure TESTING is not set
        os.environ.pop("TESTING", None)

        app = create_app()

        assert app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] is False
        assert app.config["JSON_SORT_KEYS"] is False
        assert "SECRET_KEY" in app.config

    @pytest.mark.unit
    def test_create_app_secret_key_from_env(self):
        """Test that SECRET_KEY can be set from environment."""
        os.environ["SECRET_KEY"] = "test-secret-key-123"
        app = create_app()

        assert app.config["SECRET_KEY"] == "test-secret-key-123"

        # Clean up
        os.environ.pop("SECRET_KEY")

    @pytest.mark.unit
    def test_create_app_default_secret_key(self):
        """Test that default SECRET_KEY is set if not in environment."""
        os.environ.pop("SECRET_KEY", None)
        app = create_app()

        assert app.config["SECRET_KEY"] == "dev-secret-key-change-me"

    @pytest.mark.unit
    def test_create_app_database_uri_from_env(self):
        """Test that SQLALCHEMY_DATABASE_URI can be set from environment."""
        os.environ["SQLALCHEMY_DATABASE_URI"] = "sqlite:///custom.db"
        os.environ.pop("TESTING", None)  # Ensure not in testing mode

        app = create_app()

        assert app.config["SQLALCHEMY_DATABASE_URI"] == "sqlite:///custom.db"

        # Clean up
        os.environ.pop("SQLALCHEMY_DATABASE_URI")

    @pytest.mark.unit
    def test_create_app_default_database_uri(self):
        """Test default database URI."""
        os.environ.pop("SQLALCHEMY_DATABASE_URI", None)
        os.environ.pop("TESTING", None)

        app = create_app()

        assert app.config["SQLALCHEMY_DATABASE_URI"] == "sqlite:///logbook.db"


class TestExtensionInitialization:
    """Test suite for Flask extension initialization."""

    @pytest.mark.unit
    def test_db_extension_initialized(self, app):
        """Test that SQLAlchemy extension is initialized."""
        # Extension should be initialized with the app
        # In Flask-SQLAlchemy 3.x, check via app.extensions instead
        assert 'sqlalchemy' in app.extensions

    @pytest.mark.unit
    def test_migrate_extension_initialized(self, app):
        """Test that Flask-Migrate extension is initialized."""
        # Check that migrate has been initialized
        # Flask-Migrate adds 'migrate' to app.extensions
        assert 'migrate' in app.extensions


class TestBlueprintRegistration:
    """Test suite for blueprint registration."""

    @pytest.mark.unit
    def test_api_blueprint_registered(self, app):
        """Test that API blueprint is registered."""
        # Check that blueprint is registered
        blueprints = [bp.name for bp in app.blueprints.values()]
        assert "api" in blueprints

    @pytest.mark.unit
    def test_api_blueprint_url_prefix(self, client):
        """Test that API blueprint has correct URL prefix."""
        # Test that /api routes are accessible
        # We'll use the enlist endpoint as it doesn't require auth
        response = client.post(
            "/api/auth/enlist",
            json={"username": "test", "email": "test@test.com", "password": "pass"}
        )
        # Should get 201 (success) or 4xx (validation error), not 404
        assert response.status_code != 404


class TestRootEndpoints:
    """Test suite for root application endpoints."""

    @pytest.mark.unit
    def test_index_endpoint(self, client):
        """Test GET / endpoint returns API information."""
        response = client.get("/")

        assert response.status_code == 200
        data = response.get_json()

        # Check JSON:API format
        assert "data" in data
        assert data["data"]["type"] == "api-info"
        assert data["data"]["id"] == "1"

        # Check attributes
        attrs = data["data"]["attributes"]
        assert attrs["message"] == "Logbook API"
        assert attrs["version"] == "1.0.0"
        assert attrs["endpoints"] == "/api"

    @pytest.mark.unit
    def test_health_endpoint(self, client):
        """Test GET /health endpoint."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.get_json()

        # Check JSON:API format
        assert "data" in data
        assert data["data"]["type"] == "health-status"
        assert data["data"]["id"] == "1"

        # Check attributes
        attrs = data["data"]["attributes"]
        assert attrs["status"] == "healthy"

    @pytest.mark.unit
    def test_index_returns_json(self, client):
        """Test that index endpoint returns JSON."""
        response = client.get("/")
        assert response.content_type == "application/json"

    @pytest.mark.unit
    def test_health_returns_json(self, client):
        """Test that health endpoint returns JSON."""
        response = client.get("/health")
        assert response.content_type == "application/json"


class TestShellContext:
    """Test suite for Flask shell context."""

    @pytest.mark.unit
    def test_shell_context_processor(self, app):
        """Test that shell context processor adds db and models."""
        with app.app_context():
            shell_context = {}
            # Get all shell context processors
            for func in app.shell_context_processors:
                shell_context.update(func())

            # Check that db and models are in context
            assert "db" in shell_context
            assert "Scribe" in shell_context
            assert "Entry" in shell_context

            # Verify they are the correct objects
            from apiserver.extensions import db as app_db
            from apiserver.models import Scribe, Entry

            assert shell_context["db"] == app_db
            assert shell_context["Scribe"] == Scribe
            assert shell_context["Entry"] == Entry


class TestApplicationConfiguration:
    """Test suite for application configuration edge cases."""

    @pytest.mark.unit
    def test_json_sort_keys_disabled(self, app):
        """Test that JSON keys are not sorted (preserves order)."""
        assert app.config["JSON_SORT_KEYS"] is False

    @pytest.mark.unit
    def test_sqlalchemy_track_modifications_disabled(self, app):
        """Test that SQLAlchemy modification tracking is disabled."""
        # This should be False to avoid warnings and improve performance
        assert app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] is False

    @pytest.mark.unit
    def test_multiple_app_instances_independent(self):
        """Test that multiple app instances are independent."""
        app1 = create_app()
        app2 = create_app()

        # They should be different instances
        assert app1 is not app2

        # They should have independent configs
        app1.config["TEST_VALUE"] = "app1"
        app2.config["TEST_VALUE"] = "app2"

        assert app1.config["TEST_VALUE"] != app2.config["TEST_VALUE"]

    @pytest.mark.unit
    def test_app_name(self, app):
        """Test that app has correct name."""
        # Flask uses the module name including path
        assert app.name == "apiserver.run"


class TestDatabaseInitialization:
    """Test suite for database initialization."""

    @pytest.mark.unit
    def test_database_tables_created(self, app, db):
        """Test that database tables are created."""
        # Get table names from database metadata
        table_names = db.metadata.tables.keys()

        assert "scribes" in table_names
        assert "entries" in table_names

    @pytest.mark.unit
    def test_can_create_scribe(self, app, db):
        """Test that Scribe model works with database."""
        from apiserver.models import Scribe

        scribe = Scribe(username="dbtest", email="dbtest@example.com")
        scribe.set_password("testpass")

        db.session.add(scribe)
        db.session.commit()

        # Verify scribe was saved
        saved_scribe = Scribe.query.filter_by(username="dbtest").first()
        assert saved_scribe is not None
        assert saved_scribe.email == "dbtest@example.com"

    @pytest.mark.unit
    def test_can_create_entry(self, app, db, sample_scribe):
        """Test that Entry model works with database."""
        from apiserver.models import Entry

        entry = Entry(content="Test entry", scribe_id=sample_scribe.id)
        db.session.add(entry)
        db.session.commit()

        # Verify entry was saved
        saved_entry = Entry.query.filter_by(content="Test entry").first()
        assert saved_entry is not None
        assert saved_entry.scribe_id == sample_scribe.id
