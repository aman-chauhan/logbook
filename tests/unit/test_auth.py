"""Unit tests for authentication decorators.

Tests for authentication utilities including:
- @require_auth decorator
- @optional_auth decorator
- HTTP Basic Auth handling
- Error responses
"""

import pytest
import base64
from flask import jsonify
from apiserver.auth import require_auth, optional_auth


class TestRequireAuthDecorator:
    """Test suite for @require_auth decorator."""

    @pytest.mark.unit
    def test_require_auth_with_valid_credentials(self, app, client, sample_scribe):
        """Test that valid credentials allow access to protected route."""
        # Create a test route with @require_auth
        @app.route("/test-protected")
        @require_auth
        def protected_route(current_scribe):
            return jsonify({"username": current_scribe.username})

        # Make request with valid credentials
        credentials = base64.b64encode(b"testuser:testpass123").decode("utf-8")
        response = client.get(
            "/test-protected",
            headers={"Authorization": f"Basic {credentials}"}
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["username"] == "testuser"

    @pytest.mark.unit
    def test_require_auth_without_credentials(self, app, client):
        """Test that missing credentials return 401."""
        # Create a test route with @require_auth
        @app.route("/test-protected")
        @require_auth
        def protected_route(current_scribe):
            return jsonify({"username": current_scribe.username})

        # Make request without credentials
        response = client.get("/test-protected")

        assert response.status_code == 401
        data = response.get_json()
        assert "errors" in data
        assert data["errors"][0]["status"] == "401"
        assert data["errors"][0]["title"] == "Authentication Required"
        assert "must provide valid credentials" in data["errors"][0]["detail"]

    @pytest.mark.unit
    def test_require_auth_with_invalid_username(self, app, client, sample_scribe):
        """Test that invalid username returns 401."""
        # Create a test route with @require_auth
        @app.route("/test-protected")
        @require_auth
        def protected_route(current_scribe):
            return jsonify({"username": current_scribe.username})

        # Make request with invalid username
        credentials = base64.b64encode(b"wronguser:testpass123").decode("utf-8")
        response = client.get(
            "/test-protected",
            headers={"Authorization": f"Basic {credentials}"}
        )

        assert response.status_code == 401
        data = response.get_json()
        assert "errors" in data
        assert data["errors"][0]["status"] == "401"
        assert data["errors"][0]["title"] == "Invalid Credentials"
        assert "username or password provided is incorrect" in data["errors"][0]["detail"]

    @pytest.mark.unit
    def test_require_auth_with_invalid_password(self, app, client, sample_scribe):
        """Test that invalid password returns 401."""
        # Create a test route with @require_auth
        @app.route("/test-protected")
        @require_auth
        def protected_route(current_scribe):
            return jsonify({"username": current_scribe.username})

        # Make request with invalid password
        credentials = base64.b64encode(b"testuser:wrongpass").decode("utf-8")
        response = client.get(
            "/test-protected",
            headers={"Authorization": f"Basic {credentials}"}
        )

        assert response.status_code == 401
        data = response.get_json()
        assert "errors" in data
        assert data["errors"][0]["status"] == "401"
        assert data["errors"][0]["title"] == "Invalid Credentials"

    @pytest.mark.unit
    def test_require_auth_scribe_passed_to_function(self, app, client, sample_scribe):
        """Test that authenticated scribe is passed to decorated function."""
        # Create a test route that uses the scribe parameter
        @app.route("/test-scribe-info")
        @require_auth
        def scribe_info(current_scribe):
            return jsonify({
                "id": current_scribe.id,
                "username": current_scribe.username,
                "email": current_scribe.email
            })

        # Make request with valid credentials
        credentials = base64.b64encode(b"testuser:testpass123").decode("utf-8")
        response = client.get(
            "/test-scribe-info",
            headers={"Authorization": f"Basic {credentials}"}
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["id"] == sample_scribe.id
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"

    @pytest.mark.unit
    def test_require_auth_with_malformed_header(self, app, client):
        """Test that malformed Authorization header returns 401."""
        # Create a test route with @require_auth
        @app.route("/test-protected")
        @require_auth
        def protected_route(current_scribe):
            return jsonify({"username": current_scribe.username})

        # Make request with malformed header (missing "Basic" prefix)
        credentials = base64.b64encode(b"testuser:testpass123").decode("utf-8")
        response = client.get(
            "/test-protected",
            headers={"Authorization": credentials}
        )

        assert response.status_code == 401

    @pytest.mark.unit
    def test_require_auth_preserves_function_metadata(self, app):
        """Test that @require_auth preserves decorated function metadata."""
        @require_auth
        def test_function(current_scribe):
            """Test function docstring."""
            pass

        # functools.wraps should preserve function name and docstring
        assert test_function.__name__ == "test_function"
        assert test_function.__doc__ == "Test function docstring."


class TestOptionalAuthDecorator:
    """Test suite for @optional_auth decorator."""

    @pytest.mark.unit
    def test_optional_auth_with_valid_credentials(self, app, client, sample_scribe):
        """Test that valid credentials pass authenticated scribe."""
        # Create a test route with @optional_auth
        @app.route("/test-optional")
        @optional_auth
        def optional_route(current_scribe):
            if current_scribe:
                return jsonify({"authenticated": True, "username": current_scribe.username})
            return jsonify({"authenticated": False})

        # Make request with valid credentials
        credentials = base64.b64encode(b"testuser:testpass123").decode("utf-8")
        response = client.get(
            "/test-optional",
            headers={"Authorization": f"Basic {credentials}"}
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["authenticated"] is True
        assert data["username"] == "testuser"

    @pytest.mark.unit
    def test_optional_auth_without_credentials(self, app, client):
        """Test that missing credentials pass None (no error)."""
        # Create a test route with @optional_auth
        @app.route("/test-optional")
        @optional_auth
        def optional_route(current_scribe):
            if current_scribe:
                return jsonify({"authenticated": True, "username": current_scribe.username})
            return jsonify({"authenticated": False})

        # Make request without credentials
        response = client.get("/test-optional")

        assert response.status_code == 200
        data = response.get_json()
        assert data["authenticated"] is False

    @pytest.mark.unit
    def test_optional_auth_with_invalid_credentials(self, app, client, sample_scribe):
        """Test that invalid credentials pass None (no error)."""
        # Create a test route with @optional_auth
        @app.route("/test-optional")
        @optional_auth
        def optional_route(current_scribe):
            if current_scribe:
                return jsonify({"authenticated": True, "username": current_scribe.username})
            return jsonify({"authenticated": False})

        # Make request with invalid credentials
        credentials = base64.b64encode(b"wronguser:wrongpass").decode("utf-8")
        response = client.get(
            "/test-optional",
            headers={"Authorization": f"Basic {credentials}"}
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["authenticated"] is False

    @pytest.mark.unit
    def test_optional_auth_allows_different_behavior(self, app, client, sample_scribe):
        """Test that optional auth enables different behavior for auth vs non-auth."""
        # Create a test route that behaves differently based on auth
        @app.route("/test-content")
        @optional_auth
        def content_route(current_scribe):
            if current_scribe:
                return jsonify({
                    "message": "Welcome back!",
                    "user": current_scribe.username
                })
            return jsonify({"message": "Hello, guest!"})

        # Test without auth
        response = client.get("/test-content")
        assert response.status_code == 200
        data = response.get_json()
        assert data["message"] == "Hello, guest!"
        assert "user" not in data

        # Test with auth
        credentials = base64.b64encode(b"testuser:testpass123").decode("utf-8")
        response = client.get(
            "/test-content",
            headers={"Authorization": f"Basic {credentials}"}
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["message"] == "Welcome back!"
        assert data["user"] == "testuser"

    @pytest.mark.unit
    def test_optional_auth_with_invalid_username(self, app, client, sample_scribe):
        """Test that invalid username passes None (not an error)."""
        # Create a test route with @optional_auth
        @app.route("/test-optional")
        @optional_auth
        def optional_route(current_scribe):
            return jsonify({"scribe": current_scribe is not None})

        # Make request with invalid username
        credentials = base64.b64encode(b"nonexistent:anypass").decode("utf-8")
        response = client.get(
            "/test-optional",
            headers={"Authorization": f"Basic {credentials}"}
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["scribe"] is False

    @pytest.mark.unit
    def test_optional_auth_with_invalid_password(self, app, client, sample_scribe):
        """Test that invalid password passes None (not an error)."""
        # Create a test route with @optional_auth
        @app.route("/test-optional")
        @optional_auth
        def optional_route(current_scribe):
            return jsonify({"scribe": current_scribe is not None})

        # Make request with valid username but wrong password
        credentials = base64.b64encode(b"testuser:wrongpass").decode("utf-8")
        response = client.get(
            "/test-optional",
            headers={"Authorization": f"Basic {credentials}"}
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["scribe"] is False

    @pytest.mark.unit
    def test_optional_auth_preserves_function_metadata(self, app):
        """Test that @optional_auth preserves decorated function metadata."""
        @optional_auth
        def test_function(current_scribe):
            """Test function docstring."""
            pass

        # functools.wraps should preserve function name and docstring
        assert test_function.__name__ == "test_function"
        assert test_function.__doc__ == "Test function docstring."
