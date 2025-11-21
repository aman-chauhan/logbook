"""Unit tests for scribe profile endpoints.

This module tests the scribe profile management endpoints:
- GET /api/scribes/<id> - View scribe profile (public)
- PATCH /api/scribes/<id> - Update own profile (authenticated)
- DELETE /api/scribes/<id> - Delete own account (authenticated)
"""

import pytest
import base64
from apiserver.models import Scribe, Entry


@pytest.mark.unit
class TestGetScribeEndpoint:
    """Test suite for GET /api/scribes/<id> endpoint."""

    def test_get_scribe_success(self, client, sample_scribe):
        """Test successfully retrieving a scribe profile."""
        response = client.get(f"/api/scribes/{sample_scribe.id}")

        assert response.status_code == 200
        data = response.get_json()
        assert "data" in data
        assert data["data"]["type"] == "scribes"
        assert data["data"]["id"] == str(sample_scribe.id)
        assert data["data"]["attributes"]["username"] == sample_scribe.username
        assert data["data"]["attributes"]["email"] == sample_scribe.email
        assert data["data"]["attributes"]["bio"] == sample_scribe.bio
        assert "createdAt" in data["data"]["attributes"]
        assert "updatedAt" in data["data"]["attributes"]

    def test_get_scribe_not_found(self, client):
        """Test retrieving a non-existent scribe returns 404."""
        fake_uuid = "00000000-0000-0000-0000-000000000000"
        response = client.get(f"/api/scribes/{fake_uuid}")

        assert response.status_code == 404
        data = response.get_json()
        assert "errors" in data
        assert len(data["errors"]) == 1
        assert data["errors"][0]["status"] == "404"
        assert data["errors"][0]["title"] == "Scribe Not Found"
        assert fake_uuid in data["errors"][0]["detail"]

    def test_get_scribe_with_bio(self, client, db, faker):
        """Test retrieving a scribe with bio information."""
        scribe = Scribe(
            username=faker.user_name(),
            email=faker.email(),
            bio="This is my bio"
        )
        scribe.set_password("testpass")
        db.session.add(scribe)
        db.session.commit()

        response = client.get(f"/api/scribes/{scribe.id}")

        assert response.status_code == 200
        data = response.get_json()
        assert data["data"]["attributes"]["bio"] == "This is my bio"

    def test_get_scribe_without_bio(self, client, sample_scribe):
        """Test retrieving a scribe without bio returns null."""
        response = client.get(f"/api/scribes/{sample_scribe.id}")

        assert response.status_code == 200
        data = response.get_json()
        assert data["data"]["attributes"]["bio"] is None

    def test_get_scribe_jsonapi_format(self, client, sample_scribe):
        """Test that response follows JSON:API specification."""
        response = client.get(f"/api/scribes/{sample_scribe.id}")

        assert response.status_code == 200
        data = response.get_json()

        # Verify JSON:API structure
        assert "data" in data
        assert "type" in data["data"]
        assert "id" in data["data"]
        assert "attributes" in data["data"]

        # Verify ID is string (JSON:API requirement)
        assert isinstance(data["data"]["id"], str)

        # Verify camelCase attribute names
        attributes = data["data"]["attributes"]
        assert "createdAt" in attributes
        assert "updatedAt" in attributes


@pytest.mark.unit
class TestUpdateScribeEndpoint:
    """Test suite for PATCH /api/scribes/<id> endpoint."""

    def test_update_scribe_email_success(self, client, sample_scribe, auth_headers, db):
        """Test successfully updating scribe email."""
        new_email = "newemail@example.com"
        response = client.patch(
            f"/api/scribes/{sample_scribe.id}",
            json={"email": new_email},
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["data"]["attributes"]["email"] == new_email

        # Verify database was updated
        db.session.expire_all()
        updated_scribe = db.session.get(Scribe, sample_scribe.id)
        assert updated_scribe.email == new_email

    def test_update_scribe_bio_success(self, client, sample_scribe, auth_headers):
        """Test successfully updating scribe bio."""
        new_bio = "This is my updated bio"
        response = client.patch(
            f"/api/scribes/{sample_scribe.id}",
            json={"bio": new_bio},
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["data"]["attributes"]["bio"] == new_bio

    def test_update_scribe_password_success(self, client, sample_scribe, auth_headers, db):
        """Test successfully updating scribe password."""
        new_password = "newpassword456"
        response = client.patch(
            f"/api/scribes/{sample_scribe.id}",
            json={"password": new_password},
            headers=auth_headers
        )

        assert response.status_code == 200

        # Verify password was updated by trying to authenticate with new password
        db.session.expire_all()
        updated_scribe = db.session.get(Scribe, sample_scribe.id)
        assert updated_scribe.check_password(new_password)
        assert not updated_scribe.check_password("testpass123")

    def test_update_scribe_multiple_fields(self, client, sample_scribe, auth_headers):
        """Test updating multiple fields at once."""
        updates = {
            "email": "multiple@example.com",
            "bio": "Updated bio",
            "password": "newpass789"
        }
        response = client.patch(
            f"/api/scribes/{sample_scribe.id}",
            json=updates,
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["data"]["attributes"]["email"] == "multiple@example.com"
        assert data["data"]["attributes"]["bio"] == "Updated bio"

    def test_update_scribe_no_auth(self, client, sample_scribe):
        """Test updating scribe without authentication returns 401."""
        response = client.patch(
            f"/api/scribes/{sample_scribe.id}",
            json={"bio": "Should fail"}
        )

        assert response.status_code == 401
        data = response.get_json()
        assert "errors" in data
        assert data["errors"][0]["status"] == "401"

    def test_update_scribe_invalid_credentials(self, client, sample_scribe):
        """Test updating scribe with wrong credentials returns 401."""
        bad_creds = base64.b64encode(
            f"{sample_scribe.username}:wrongpassword".encode()
        ).decode("utf-8")
        headers = {"Authorization": f"Basic {bad_creds}"}

        response = client.patch(
            f"/api/scribes/{sample_scribe.id}",
            json={"bio": "Should fail"},
            headers=headers
        )

        assert response.status_code == 401

    def test_update_scribe_other_user(self, client, db, scribe_factory, auth_headers):
        """Test updating another scribe's profile returns 403."""
        other_scribe = scribe_factory()

        response = client.patch(
            f"/api/scribes/{other_scribe.id}",
            json={"bio": "Should fail"},
            headers=auth_headers
        )

        assert response.status_code == 403
        data = response.get_json()
        assert "errors" in data
        assert data["errors"][0]["status"] == "403"
        assert data["errors"][0]["title"] == "Forbidden"
        assert "your own profile" in data["errors"][0]["detail"]

    def test_update_scribe_not_found(self, client, auth_headers):
        """Test updating non-existent scribe returns 404."""
        fake_uuid = "00000000-0000-0000-0000-000000000000"
        response = client.patch(
            f"/api/scribes/{fake_uuid}",
            json={"bio": "Should fail"},
            headers=auth_headers
        )

        assert response.status_code == 404
        data = response.get_json()
        assert data["errors"][0]["status"] == "404"

    def test_update_scribe_no_json_body(self, client, sample_scribe, auth_headers):
        """Test updating scribe without JSON body returns 415 Unsupported Media Type."""
        response = client.patch(
            f"/api/scribes/{sample_scribe.id}",
            headers=auth_headers
        )

        # Flask returns 415 when Content-Type header is missing or incorrect
        assert response.status_code == 415

    def test_update_scribe_duplicate_email(self, client, db, sample_scribe, auth_headers, scribe_factory):
        """Test updating to an existing email returns 409."""
        scribe_factory(email="taken@example.com")

        response = client.patch(
            f"/api/scribes/{sample_scribe.id}",
            json={"email": "taken@example.com"},
            headers=auth_headers
        )

        assert response.status_code == 409
        data = response.get_json()
        assert data["errors"][0]["status"] == "409"
        assert data["errors"][0]["title"] == "Email Already Exists"
        assert "taken@example.com" in data["errors"][0]["detail"]

    def test_update_scribe_same_email(self, client, sample_scribe, auth_headers):
        """Test updating to the same email (no change) succeeds."""
        response = client.patch(
            f"/api/scribes/{sample_scribe.id}",
            json={"email": sample_scribe.email},
            headers=auth_headers
        )

        assert response.status_code == 200

    def test_update_scribe_empty_bio(self, client, sample_scribe, auth_headers):
        """Test setting bio to empty string."""
        response = client.patch(
            f"/api/scribes/{sample_scribe.id}",
            json={"bio": ""},
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["data"]["attributes"]["bio"] == ""

    def test_update_scribe_null_bio(self, client, sample_scribe, auth_headers):
        """Test setting bio to null."""
        response = client.patch(
            f"/api/scribes/{sample_scribe.id}",
            json={"bio": None},
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["data"]["attributes"]["bio"] is None


@pytest.mark.unit
class TestDeleteScribeEndpoint:
    """Test suite for DELETE /api/scribes/<id> endpoint."""

    def test_delete_scribe_success(self, client, sample_scribe, auth_headers, db):
        """Test successfully deleting own scribe account."""
        scribe_id = sample_scribe.id

        response = client.delete(
            f"/api/scribes/{scribe_id}",
            headers=auth_headers
        )

        assert response.status_code == 204
        assert response.data == b""

        # Verify scribe was deleted from database
        deleted_scribe = db.session.get(Scribe, scribe_id)
        assert deleted_scribe is None

    def test_delete_scribe_cascade_deletes_entries(self, client, sample_scribe, sample_entry, auth_headers, db):
        """Test deleting scribe cascades to delete all their entries."""
        scribe_id = sample_scribe.id
        entry_id = sample_entry.id

        # Verify entry exists before deletion
        entry = db.session.get(Entry, entry_id)
        assert entry is not None
        assert entry.scribe_id == scribe_id

        response = client.delete(
            f"/api/scribes/{scribe_id}",
            headers=auth_headers
        )

        assert response.status_code == 204

        # Verify entry was cascade deleted
        deleted_entry = db.session.get(Entry, entry_id)
        assert deleted_entry is None

    def test_delete_scribe_with_multiple_entries(self, client, sample_scribe, auth_headers, entry_factory, db):
        """Test deleting scribe with multiple entries cascades all deletions."""
        # Create multiple entries for the scribe
        entry1 = entry_factory(sample_scribe.id)
        entry2 = entry_factory(sample_scribe.id)
        entry3 = entry_factory(sample_scribe.id)

        entry_ids = [entry1.id, entry2.id, entry3.id]
        scribe_id = sample_scribe.id

        response = client.delete(
            f"/api/scribes/{scribe_id}",
            headers=auth_headers
        )

        assert response.status_code == 204

        # Verify all entries were cascade deleted
        for entry_id in entry_ids:
            deleted_entry = db.session.get(Entry, entry_id)
            assert deleted_entry is None

    def test_delete_scribe_no_auth(self, client, sample_scribe):
        """Test deleting scribe without authentication returns 401."""
        response = client.delete(f"/api/scribes/{sample_scribe.id}")

        assert response.status_code == 401
        data = response.get_json()
        assert data["errors"][0]["status"] == "401"

    def test_delete_scribe_invalid_credentials(self, client, sample_scribe):
        """Test deleting scribe with wrong credentials returns 401."""
        bad_creds = base64.b64encode(
            f"{sample_scribe.username}:wrongpassword".encode()
        ).decode("utf-8")
        headers = {"Authorization": f"Basic {bad_creds}"}

        response = client.delete(
            f"/api/scribes/{sample_scribe.id}",
            headers=headers
        )

        assert response.status_code == 401

    def test_delete_scribe_other_user(self, client, scribe_factory, auth_headers):
        """Test deleting another scribe's account returns 403."""
        other_scribe = scribe_factory()

        response = client.delete(
            f"/api/scribes/{other_scribe.id}",
            headers=auth_headers
        )

        assert response.status_code == 403
        data = response.get_json()
        assert data["errors"][0]["status"] == "403"
        assert data["errors"][0]["title"] == "Forbidden"
        assert "your own account" in data["errors"][0]["detail"]

    def test_delete_scribe_not_found(self, client, auth_headers):
        """Test deleting non-existent scribe returns 404."""
        fake_uuid = "00000000-0000-0000-0000-000000000000"
        response = client.delete(
            f"/api/scribes/{fake_uuid}",
            headers=auth_headers
        )

        assert response.status_code == 404
        data = response.get_json()
        assert data["errors"][0]["status"] == "404"
        assert data["errors"][0]["title"] == "Scribe Not Found"

    def test_delete_scribe_cannot_authenticate_after_deletion(self, client, sample_scribe, auth_headers, db):
        """Test that deleted scribe cannot authenticate anymore."""
        username = sample_scribe.username

        # Delete the scribe
        response = client.delete(
            f"/api/scribes/{sample_scribe.id}",
            headers=auth_headers
        )
        assert response.status_code == 204

        # Try to authenticate with deleted scribe credentials
        creds = base64.b64encode(f"{username}:testpass123".encode()).decode("utf-8")
        headers = {"Authorization": f"Basic {creds}"}

        response = client.post("/api/auth/unlock", headers=headers)
        assert response.status_code == 401
