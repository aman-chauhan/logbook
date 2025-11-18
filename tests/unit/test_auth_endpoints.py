"""Unit tests for authentication endpoints.

Tests for authentication API endpoints:
- POST /api/auth/enlist (registration)
- POST /api/auth/unlock (login)
- POST /api/auth/lock (logout)
"""

import pytest
import base64
from apiserver.models import Scribe


class TestEnlistEndpoint:
    """Test suite for POST /api/auth/enlist endpoint."""

    @pytest.mark.unit
    def test_enlist_success(self, client, db, faker):
        """Test successful user registration."""
        username = faker.user_name()
        email = faker.email()
        password = faker.password()

        response = client.post(
            "/api/auth/enlist",
            json={
                "username": username,
                "email": email,
                "password": password
            },
            headers={"Content-Type": "application/json"}
        )

        assert response.status_code == 201
        data = response.get_json()

        # Check JSON:API format
        assert "data" in data
        assert data["data"]["type"] == "scribes"
        assert data["data"]["id"] is not None

        # Check attributes
        attrs = data["data"]["attributes"]
        assert attrs["username"] == username
        assert attrs["email"] == email
        assert "createdAt" in attrs
        assert "updatedAt" in attrs

        # Verify password is not in response
        assert "password" not in attrs
        assert "passwordHash" not in attrs

        # Verify user was created in database
        scribe = Scribe.query.filter_by(username=username).first()
        assert scribe is not None
        assert scribe.email == email
        assert scribe.check_password(password)

    @pytest.mark.unit
    def test_enlist_with_bio(self, client, db, faker):
        """Test registration with optional bio field."""
        username = faker.user_name()
        email = faker.email()
        password = faker.password()
        bio = faker.sentence()

        response = client.post(
            "/api/auth/enlist",
            json={
                "username": username,
                "email": email,
                "password": password,
                "bio": bio
            },
            headers={"Content-Type": "application/json"}
        )

        assert response.status_code == 201
        data = response.get_json()
        assert data["data"]["attributes"]["bio"] == bio

        # Verify in database
        scribe = Scribe.query.filter_by(username=username).first()
        assert scribe.bio == bio

    @pytest.mark.unit
    def test_enlist_missing_username(self, client, faker):
        """Test registration fails when username is missing."""
        response = client.post(
            "/api/auth/enlist",
            json={
                "email": faker.email(),
                "password": faker.password()
            },
            headers={"Content-Type": "application/json"}
        )

        assert response.status_code == 400
        data = response.get_json()
        assert "errors" in data
        assert data["errors"][0]["status"] == "400"
        assert data["errors"][0]["title"] == "Missing Required Fields"
        assert "username" in data["errors"][0]["detail"]

    @pytest.mark.unit
    def test_enlist_missing_email(self, client, faker):
        """Test registration fails when email is missing."""
        response = client.post(
            "/api/auth/enlist",
            json={
                "username": faker.user_name(),
                "password": faker.password()
            },
            headers={"Content-Type": "application/json"}
        )

        assert response.status_code == 400
        data = response.get_json()
        assert "errors" in data
        assert "email" in data["errors"][0]["detail"]

    @pytest.mark.unit
    def test_enlist_missing_password(self, client, faker):
        """Test registration fails when password is missing."""
        response = client.post(
            "/api/auth/enlist",
            json={
                "username": faker.user_name(),
                "email": faker.email()
            },
            headers={"Content-Type": "application/json"}
        )

        assert response.status_code == 400
        data = response.get_json()
        assert "errors" in data
        assert "password" in data["errors"][0]["detail"]

    @pytest.mark.unit
    def test_enlist_missing_multiple_fields(self, client):
        """Test registration fails with multiple missing fields."""
        # Note: Empty dict {} is falsy in Python, so it triggers "Invalid Request" error
        # To test missing fields, we need to send a non-empty dict with some fields
        response = client.post(
            "/api/auth/enlist",
            json={"bio": "test"},  # Missing required fields
            headers={"Content-Type": "application/json"}
        )

        assert response.status_code == 400
        data = response.get_json()
        assert "errors" in data
        detail = data["errors"][0]["detail"]
        assert "username" in detail
        assert "email" in detail
        assert "password" in detail

    @pytest.mark.unit
    def test_enlist_duplicate_username(self, client, sample_scribe, faker):
        """Test registration fails with duplicate username."""
        response = client.post(
            "/api/auth/enlist",
            json={
                "username": sample_scribe.username,  # Already exists
                "email": faker.email(),
                "password": faker.password()
            },
            headers={"Content-Type": "application/json"}
        )

        assert response.status_code == 409
        data = response.get_json()
        assert "errors" in data
        assert data["errors"][0]["status"] == "409"
        assert data["errors"][0]["title"] == "Username Already Exists"
        assert sample_scribe.username in data["errors"][0]["detail"]

    @pytest.mark.unit
    def test_enlist_duplicate_email(self, client, sample_scribe, faker):
        """Test registration fails with duplicate email."""
        response = client.post(
            "/api/auth/enlist",
            json={
                "username": faker.user_name(),
                "email": sample_scribe.email,  # Already exists
                "password": faker.password()
            },
            headers={"Content-Type": "application/json"}
        )

        assert response.status_code == 409
        data = response.get_json()
        assert "errors" in data
        assert data["errors"][0]["status"] == "409"
        assert data["errors"][0]["title"] == "Email Already Exists"
        assert sample_scribe.email in data["errors"][0]["detail"]

    @pytest.mark.unit
    def test_enlist_invalid_json(self, client):
        """Test registration fails with invalid JSON."""
        response = client.post(
            "/api/auth/enlist",
            data="not json",
            headers={"Content-Type": "application/json"}
        )

        assert response.status_code == 400
        # Flask may return a different error for malformed JSON before it reaches our handler
        # Check that we got an error response
        data = response.get_json(force=True, silent=True)
        if data is None:
            # Flask returned a non-JSON error (e.g., 400 Bad Request for malformed JSON)
            assert True  # This is acceptable - Flask caught the error
        else:
            # Our endpoint handled it
            assert "errors" in data
            assert data["errors"][0]["title"] == "Invalid Request"

    @pytest.mark.unit
    def test_enlist_null_json_body(self, client):
        """Test registration fails with null/empty JSON body."""
        response = client.post(
            "/api/auth/enlist",
            headers={"Content-Type": "application/json"}
        )

        assert response.status_code == 400
        # When no body is provided, Flask may return different errors
        data = response.get_json(force=True, silent=True)
        if data is None:
            # Flask returned a non-JSON error
            assert True  # This is acceptable
        else:
            # Our endpoint handled it
            assert "errors" in data
            assert data["errors"][0]["title"] == "Invalid Request"

    @pytest.mark.unit
    def test_enlist_password_is_hashed(self, client, db, faker):
        """Test that password is properly hashed in database."""
        username = faker.user_name()
        email = faker.email()
        password = faker.password()

        response = client.post(
            "/api/auth/enlist",
            json={
                "username": username,
                "email": email,
                "password": password
            },
            headers={"Content-Type": "application/json"}
        )

        assert response.status_code == 201

        # Verify password is hashed in database
        scribe = Scribe.query.filter_by(username=username).first()
        assert scribe.password_hash != password
        assert isinstance(scribe.password_hash, str) and scribe.password_hash
        assert scribe.check_password(password)


class TestUnlockEndpoint:
    """Test suite for POST /api/auth/unlock endpoint."""

    @pytest.mark.unit
    def test_unlock_success(self, client, sample_scribe):
        """Test successful login with valid credentials."""
        credentials = base64.b64encode(
            f"{sample_scribe.username}:testpass123".encode()
        ).decode("utf-8")
        response = client.post(
            "/api/auth/unlock",
            headers={"Authorization": f"Basic {credentials}"}
        )

        assert response.status_code == 200
        data = response.get_json()

        # Check JSON:API format
        assert "data" in data
        assert data["data"]["type"] == "scribes"
        assert data["data"]["id"] == str(sample_scribe.id)

        # Check attributes
        attrs = data["data"]["attributes"]
        assert attrs["username"] == sample_scribe.username
        assert attrs["email"] == sample_scribe.email

    @pytest.mark.unit
    def test_unlock_without_credentials(self, client):
        """Test login fails without credentials."""
        response = client.post("/api/auth/unlock")

        assert response.status_code == 401
        data = response.get_json()
        assert "errors" in data
        assert data["errors"][0]["status"] == "401"
        assert data["errors"][0]["title"] == "Authentication Required"

    @pytest.mark.unit
    def test_unlock_with_invalid_username(self, client, sample_scribe, faker):
        """Test login fails with invalid username."""
        credentials = base64.b64encode(
            f"{faker.user_name()}:testpass123".encode()
        ).decode("utf-8")
        response = client.post(
            "/api/auth/unlock",
            headers={"Authorization": f"Basic {credentials}"}
        )

        assert response.status_code == 401
        data = response.get_json()
        assert "errors" in data
        assert data["errors"][0]["title"] == "Invalid Credentials"

    @pytest.mark.unit
    def test_unlock_with_invalid_password(self, client, sample_scribe, faker):
        """Test login fails with invalid password."""
        credentials = base64.b64encode(
            f"{sample_scribe.username}:{faker.password()}".encode()
        ).decode("utf-8")
        response = client.post(
            "/api/auth/unlock",
            headers={"Authorization": f"Basic {credentials}"}
        )

        assert response.status_code == 401
        data = response.get_json()
        assert "errors" in data
        assert data["errors"][0]["title"] == "Invalid Credentials"

    @pytest.mark.unit
    def test_unlock_returns_complete_profile(self, client, db, faker):
        """Test that unlock returns complete user profile."""
        # Create scribe with bio
        username = faker.user_name()
        email = faker.email()
        password = faker.password()
        bio = faker.sentence()

        scribe = Scribe(username=username, email=email, bio=bio)
        scribe.set_password(password)
        db.session.add(scribe)
        db.session.commit()

        credentials = base64.b64encode(f"{username}:{password}".encode()).decode("utf-8")
        response = client.post(
            "/api/auth/unlock",
            headers={"Authorization": f"Basic {credentials}"}
        )

        assert response.status_code == 200
        data = response.get_json()
        attrs = data["data"]["attributes"]
        assert attrs["bio"] == bio
        assert "createdAt" in attrs
        assert "updatedAt" in attrs


class TestLockEndpoint:
    """Test suite for POST /api/auth/lock endpoint."""

    @pytest.mark.unit
    def test_lock_success(self, client, sample_scribe):
        """Test successful logout."""
        credentials = base64.b64encode(
            f"{sample_scribe.username}:testpass123".encode()
        ).decode("utf-8")
        response = client.post(
            "/api/auth/lock",
            headers={"Authorization": f"Basic {credentials}"}
        )

        assert response.status_code == 204
        assert response.data == b""  # Empty response body

    @pytest.mark.unit
    def test_lock_without_credentials(self, client):
        """Test logout fails without credentials."""
        response = client.post("/api/auth/lock")

        assert response.status_code == 401
        data = response.get_json()
        assert "errors" in data
        assert data["errors"][0]["title"] == "Authentication Required"

    @pytest.mark.unit
    def test_lock_with_invalid_credentials(self, client, sample_scribe, faker):
        """Test logout fails with invalid credentials."""
        credentials = base64.b64encode(
            f"{sample_scribe.username}:{faker.password()}".encode()
        ).decode("utf-8")
        response = client.post(
            "/api/auth/lock",
            headers={"Authorization": f"Basic {credentials}"}
        )

        assert response.status_code == 401
        data = response.get_json()
        assert "errors" in data

    @pytest.mark.unit
    def test_lock_is_idempotent(self, client, sample_scribe):
        """Test that multiple logout calls are safe (idempotent)."""
        credentials = base64.b64encode(
            f"{sample_scribe.username}:testpass123".encode()
        ).decode("utf-8")
        headers = {"Authorization": f"Basic {credentials}"}

        # First logout
        response1 = client.post("/api/auth/lock", headers=headers)
        assert response1.status_code == 204

        # Second logout (should still work)
        response2 = client.post("/api/auth/lock", headers=headers)
        assert response2.status_code == 204


class TestAuthEndpointsIntegration:
    """Integration tests for auth endpoints working together."""

    @pytest.mark.unit
    def test_full_auth_flow(self, client, db, faker):
        """Test complete authentication flow: enlist -> unlock -> lock."""
        username = faker.user_name()
        email = faker.email()
        password = faker.password()

        # 1. Register new user
        enlist_response = client.post(
            "/api/auth/enlist",
            json={
                "username": username,
                "email": email,
                "password": password
            },
            headers={"Content-Type": "application/json"}
        )
        assert enlist_response.status_code == 201
        user_id = enlist_response.get_json()["data"]["id"]

        # 2. Login with new credentials
        credentials = base64.b64encode(f"{username}:{password}".encode()).decode("utf-8")
        unlock_response = client.post(
            "/api/auth/unlock",
            headers={"Authorization": f"Basic {credentials}"}
        )
        assert unlock_response.status_code == 200
        assert unlock_response.get_json()["data"]["id"] == user_id

        # 3. Logout
        lock_response = client.post(
            "/api/auth/lock",
            headers={"Authorization": f"Basic {credentials}"}
        )
        assert lock_response.status_code == 204

    @pytest.mark.unit
    def test_cannot_login_before_registration(self, client, faker):
        """Test that login fails for non-existent user."""
        credentials = base64.b64encode(
            f"{faker.user_name()}:{faker.password()}".encode()
        ).decode("utf-8")
        response = client.post(
            "/api/auth/unlock",
            headers={"Authorization": f"Basic {credentials}"}
        )
        assert response.status_code == 401

    @pytest.mark.unit
    def test_json_api_error_format(self, client):
        """Test that all error responses follow JSON:API format."""
        # Test enlist error
        response = client.post("/api/auth/enlist", json={})
        assert response.status_code == 400
        data = response.get_json()
        assert "errors" in data
        assert isinstance(data["errors"], list)
        error = data["errors"][0]
        assert "status" in error
        assert "title" in error
        assert "detail" in error

        # Test unlock error
        response = client.post("/api/auth/unlock")
        assert response.status_code == 401
        data = response.get_json()
        assert "errors" in data
        error = data["errors"][0]
        assert error["status"] == "401"
        assert "title" in error
        assert "detail" in error
