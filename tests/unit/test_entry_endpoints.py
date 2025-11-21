"""Unit tests for entry endpoints.

This module tests the entry management endpoints:
- POST /api/entries - Create a new entry
- GET /api/entries/<id> - View a single entry
- PATCH /api/entries/<id> - Update an entry
- DELETE /api/entries/<id> - Delete an entry
- GET /api/chronicle - View authenticated scribe's entries
"""

import pytest
import base64
from apiserver.models import Entry


@pytest.mark.unit
class TestCreateEntryEndpoint:
    """Test suite for POST /api/entries endpoint."""

    def test_create_entry_success(self, client, sample_scribe, auth_headers):
        """Test successfully creating a public entry."""
        entry_data = {
            "content": "This is my first entry!",
            "visibility": "public"
        }

        response = client.post(
            "/api/entries",
            json=entry_data,
            headers=auth_headers
        )

        assert response.status_code == 201
        data = response.get_json()
        assert "data" in data
        assert data["data"]["type"] == "entries"
        assert data["data"]["attributes"]["content"] == "This is my first entry!"
        assert data["data"]["attributes"]["visibility"] == "public"
        assert data["data"]["attributes"]["scribeId"] == sample_scribe.id
        assert data["data"]["attributes"]["scribeUsername"] == sample_scribe.username
        assert "createdAt" in data["data"]["attributes"]
        assert "updatedAt" in data["data"]["attributes"]

    def test_create_entry_private(self, client, sample_scribe, auth_headers):
        """Test creating a private entry."""
        entry_data = {
            "content": "This is a private entry",
            "visibility": "private"
        }

        response = client.post(
            "/api/entries",
            json=entry_data,
            headers=auth_headers
        )

        assert response.status_code == 201
        data = response.get_json()
        assert data["data"]["attributes"]["visibility"] == "private"

    def test_create_entry_default_visibility(self, client, auth_headers):
        """Test creating entry without visibility defaults to public."""
        entry_data = {"content": "Default visibility entry"}

        response = client.post(
            "/api/entries",
            json=entry_data,
            headers=auth_headers
        )

        assert response.status_code == 201
        data = response.get_json()
        assert data["data"]["attributes"]["visibility"] == "public"

    def test_create_entry_no_auth(self, client):
        """Test creating entry without authentication returns 401."""
        entry_data = {"content": "Should fail"}

        response = client.post("/api/entries", json=entry_data)

        assert response.status_code == 401
        data = response.get_json()
        assert data["errors"][0]["status"] == "401"

    def test_create_entry_invalid_credentials(self, client, sample_scribe):
        """Test creating entry with wrong credentials returns 401."""
        bad_creds = base64.b64encode(
            f"{sample_scribe.username}:wrongpassword".encode()
        ).decode("utf-8")
        headers = {"Authorization": f"Basic {bad_creds}"}

        response = client.post(
            "/api/entries",
            json={"content": "Should fail"},
            headers=headers
        )

        assert response.status_code == 401

    def test_create_entry_missing_content(self, client, auth_headers):
        """Test creating entry without content returns 400."""
        response = client.post(
            "/api/entries",
            json={"visibility": "public"},
            headers=auth_headers
        )

        assert response.status_code == 400
        data = response.get_json()
        assert data["errors"][0]["status"] == "400"
        assert data["errors"][0]["title"] == "Missing Required Field"
        assert "content" in data["errors"][0]["detail"]

    def test_create_entry_no_json_body(self, client, auth_headers):
        """Test creating entry without JSON body returns 415 Unsupported Media Type."""
        response = client.post("/api/entries", headers=auth_headers)

        # Flask returns 415 when Content-Type header is missing or incorrect
        assert response.status_code == 415

    def test_create_entry_invalid_visibility(self, client, auth_headers):
        """Test creating entry with invalid visibility returns 400."""
        entry_data = {
            "content": "Test entry",
            "visibility": "invalid"
        }

        response = client.post(
            "/api/entries",
            json=entry_data,
            headers=auth_headers
        )

        assert response.status_code == 400
        data = response.get_json()
        assert data["errors"][0]["status"] == "400"
        assert data["errors"][0]["title"] == "Invalid Visibility"
        assert "public" in data["errors"][0]["detail"]
        assert "private" in data["errors"][0]["detail"]

    def test_create_entry_long_content(self, client, auth_headers):
        """Test creating entry with long content."""
        long_content = "A" * 5000
        entry_data = {"content": long_content}

        response = client.post(
            "/api/entries",
            json=entry_data,
            headers=auth_headers
        )

        assert response.status_code == 201
        data = response.get_json()
        assert data["data"]["attributes"]["content"] == long_content

    def test_create_entry_empty_content(self, client, auth_headers):
        """Test creating entry with empty content string."""
        entry_data = {"content": ""}

        response = client.post(
            "/api/entries",
            json=entry_data,
            headers=auth_headers
        )

        # Empty content is still valid (contains the key)
        assert response.status_code == 201

    def test_create_entry_jsonapi_format(self, client, auth_headers):
        """Test that response follows JSON:API specification."""
        entry_data = {"content": "Test entry"}

        response = client.post(
            "/api/entries",
            json=entry_data,
            headers=auth_headers
        )

        assert response.status_code == 201
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
        assert "scribeId" in attributes
        assert "scribeUsername" in attributes


@pytest.mark.unit
class TestGetEntryEndpoint:
    """Test suite for GET /api/entries/<id> endpoint."""

    def test_get_public_entry_no_auth(self, client, sample_entry):
        """Test retrieving public entry without authentication."""
        response = client.get(f"/api/entries/{sample_entry.id}")

        assert response.status_code == 200
        data = response.get_json()
        assert data["data"]["id"] == str(sample_entry.id)
        assert data["data"]["attributes"]["content"] == sample_entry.content
        assert data["data"]["attributes"]["visibility"] == "public"

    def test_get_public_entry_with_auth(self, client, sample_entry, auth_headers):
        """Test retrieving public entry with authentication."""
        response = client.get(
            f"/api/entries/{sample_entry.id}",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["data"]["id"] == str(sample_entry.id)

    def test_get_private_entry_as_owner(self, client, db, sample_scribe, auth_headers):
        """Test retrieving private entry as the owner."""
        private_entry = Entry(
            content="Private entry content",
            scribe_id=sample_scribe.id,
            visibility="private"
        )
        db.session.add(private_entry)
        db.session.commit()

        response = client.get(
            f"/api/entries/{private_entry.id}",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["data"]["attributes"]["visibility"] == "private"

    def test_get_private_entry_as_non_owner(self, client, db, scribe_factory):
        """Test retrieving private entry as non-owner returns 404."""
        owner = scribe_factory()
        private_entry = Entry(
            content="Private entry",
            scribe_id=owner.id,
            visibility="private"
        )
        db.session.add(private_entry)
        db.session.commit()

        # Try to access with different user credentials
        other_user = scribe_factory()
        creds = base64.b64encode(
            f"{other_user.username}:testpass123".encode()
        ).decode("utf-8")
        headers = {"Authorization": f"Basic {creds}"}

        response = client.get(f"/api/entries/{private_entry.id}", headers=headers)

        # Returns 404 to hide existence from non-owners
        assert response.status_code == 404

    def test_get_private_entry_no_auth(self, client, db, scribe_factory):
        """Test retrieving private entry without auth returns 404."""
        owner = scribe_factory()
        private_entry = Entry(
            content="Private entry",
            scribe_id=owner.id,
            visibility="private"
        )
        db.session.add(private_entry)
        db.session.commit()

        response = client.get(f"/api/entries/{private_entry.id}")

        # Returns 404 to hide existence
        assert response.status_code == 404

    def test_get_entry_not_found(self, client):
        """Test retrieving non-existent entry returns 404."""
        fake_uuid = "00000000-0000-0000-0000-000000000000"
        response = client.get(f"/api/entries/{fake_uuid}")

        assert response.status_code == 404
        data = response.get_json()
        assert data["errors"][0]["status"] == "404"
        assert data["errors"][0]["title"] == "Entry Not Found"

    def test_get_entry_includes_scribe_info(self, client, sample_entry, sample_scribe):
        """Test that entry response includes scribe information."""
        response = client.get(f"/api/entries/{sample_entry.id}")

        assert response.status_code == 200
        data = response.get_json()
        assert data["data"]["attributes"]["scribeId"] == sample_scribe.id
        assert data["data"]["attributes"]["scribeUsername"] == sample_scribe.username


@pytest.mark.unit
class TestUpdateEntryEndpoint:
    """Test suite for PATCH /api/entries/<id> endpoint."""

    def test_update_entry_content_success(self, client, sample_entry, auth_headers, db):
        """Test successfully updating entry content."""
        new_content = "Updated content"
        response = client.patch(
            f"/api/entries/{sample_entry.id}",
            json={"content": new_content},
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["data"]["attributes"]["content"] == new_content

        # Verify database was updated
        db.session.expire_all()
        updated_entry = db.session.get(Entry, sample_entry.id)
        assert updated_entry.content == new_content

    def test_update_entry_visibility_success(self, client, sample_entry, auth_headers, db):
        """Test successfully updating entry visibility."""
        response = client.patch(
            f"/api/entries/{sample_entry.id}",
            json={"visibility": "private"},
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["data"]["attributes"]["visibility"] == "private"

    def test_update_entry_both_fields(self, client, sample_entry, auth_headers):
        """Test updating both content and visibility."""
        updates = {
            "content": "New content",
            "visibility": "private"
        }
        response = client.patch(
            f"/api/entries/{sample_entry.id}",
            json=updates,
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["data"]["attributes"]["content"] == "New content"
        assert data["data"]["attributes"]["visibility"] == "private"

    def test_update_entry_no_auth(self, client, sample_entry):
        """Test updating entry without authentication returns 401."""
        response = client.patch(
            f"/api/entries/{sample_entry.id}",
            json={"content": "Should fail"}
        )

        assert response.status_code == 401

    def test_update_entry_invalid_credentials(self, client, sample_entry, sample_scribe):
        """Test updating entry with wrong credentials returns 401."""
        bad_creds = base64.b64encode(
            f"{sample_scribe.username}:wrongpassword".encode()
        ).decode("utf-8")
        headers = {"Authorization": f"Basic {bad_creds}"}

        response = client.patch(
            f"/api/entries/{sample_entry.id}",
            json={"content": "Should fail"},
            headers=headers
        )

        assert response.status_code == 401

    def test_update_entry_other_user(self, client, db, scribe_factory):
        """Test updating another user's entry returns 403."""
        owner = scribe_factory()
        entry = Entry(content="Original", scribe_id=owner.id, visibility="public")
        db.session.add(entry)
        db.session.commit()

        # Try to update with different user
        other_user = scribe_factory()
        creds = base64.b64encode(
            f"{other_user.username}:testpass123".encode()
        ).decode("utf-8")
        headers = {"Authorization": f"Basic {creds}"}

        response = client.patch(
            f"/api/entries/{entry.id}",
            json={"content": "Should fail"},
            headers=headers
        )

        assert response.status_code == 403
        data = response.get_json()
        assert data["errors"][0]["status"] == "403"
        assert data["errors"][0]["title"] == "Forbidden"
        assert "your own entries" in data["errors"][0]["detail"]

    def test_update_entry_not_found(self, client, auth_headers):
        """Test updating non-existent entry returns 404."""
        fake_uuid = "00000000-0000-0000-0000-000000000000"
        response = client.patch(
            f"/api/entries/{fake_uuid}",
            json={"content": "Should fail"},
            headers=auth_headers
        )

        assert response.status_code == 404

    def test_update_entry_no_json_body(self, client, sample_entry, auth_headers):
        """Test updating entry without JSON body returns 415 Unsupported Media Type."""
        response = client.patch(
            f"/api/entries/{sample_entry.id}",
            headers=auth_headers
        )

        # Flask returns 415 when Content-Type header is missing or incorrect
        assert response.status_code == 415

    def test_update_entry_invalid_visibility(self, client, sample_entry, auth_headers):
        """Test updating entry with invalid visibility returns 400."""
        response = client.patch(
            f"/api/entries/{sample_entry.id}",
            json={"visibility": "invalid"},
            headers=auth_headers
        )

        assert response.status_code == 400
        data = response.get_json()
        assert data["errors"][0]["title"] == "Invalid Visibility"

    def test_update_entry_empty_updates(self, client, sample_entry, auth_headers):
        """Test updating entry with empty JSON object returns 400."""
        response = client.patch(
            f"/api/entries/{sample_entry.id}",
            json={},
            headers=auth_headers,
            content_type='application/json'
        )

        # Empty JSON object is treated as invalid by the endpoint
        assert response.status_code == 400
        data = response.get_json()
        assert data["errors"][0]["status"] == "400"
        assert "JSON" in data["errors"][0]["detail"]


@pytest.mark.unit
class TestDeleteEntryEndpoint:
    """Test suite for DELETE /api/entries/<id> endpoint."""

    def test_delete_entry_success(self, client, sample_entry, auth_headers, db):
        """Test successfully deleting own entry."""
        entry_id = sample_entry.id

        response = client.delete(
            f"/api/entries/{entry_id}",
            headers=auth_headers
        )

        assert response.status_code == 204
        assert response.data == b""

        # Verify entry was deleted from database
        deleted_entry = db.session.get(Entry, entry_id)
        assert deleted_entry is None

    def test_delete_entry_no_auth(self, client, sample_entry):
        """Test deleting entry without authentication returns 401."""
        response = client.delete(f"/api/entries/{sample_entry.id}")

        assert response.status_code == 401

    def test_delete_entry_invalid_credentials(self, client, sample_entry, sample_scribe):
        """Test deleting entry with wrong credentials returns 401."""
        bad_creds = base64.b64encode(
            f"{sample_scribe.username}:wrongpassword".encode()
        ).decode("utf-8")
        headers = {"Authorization": f"Basic {bad_creds}"}

        response = client.delete(
            f"/api/entries/{sample_entry.id}",
            headers=headers
        )

        assert response.status_code == 401

    def test_delete_entry_other_user(self, client, db, scribe_factory):
        """Test deleting another user's entry returns 403."""
        owner = scribe_factory()
        entry = Entry(content="Original", scribe_id=owner.id, visibility="public")
        db.session.add(entry)
        db.session.commit()

        # Try to delete with different user
        other_user = scribe_factory()
        creds = base64.b64encode(
            f"{other_user.username}:testpass123".encode()
        ).decode("utf-8")
        headers = {"Authorization": f"Basic {creds}"}

        response = client.delete(f"/api/entries/{entry.id}", headers=headers)

        assert response.status_code == 403
        data = response.get_json()
        assert data["errors"][0]["status"] == "403"
        assert data["errors"][0]["title"] == "Forbidden"
        assert "your own entries" in data["errors"][0]["detail"]

    def test_delete_entry_not_found(self, client, auth_headers):
        """Test deleting non-existent entry returns 404."""
        fake_uuid = "00000000-0000-0000-0000-000000000000"
        response = client.delete(f"/api/entries/{fake_uuid}", headers=auth_headers)

        assert response.status_code == 404
        data = response.get_json()
        assert data["errors"][0]["status"] == "404"

    def test_delete_private_entry(self, client, db, sample_scribe, auth_headers):
        """Test deleting a private entry."""
        private_entry = Entry(
            content="Private",
            scribe_id=sample_scribe.id,
            visibility="private"
        )
        db.session.add(private_entry)
        db.session.commit()
        entry_id = private_entry.id

        response = client.delete(
            f"/api/entries/{entry_id}",
            headers=auth_headers
        )

        assert response.status_code == 204
        assert db.session.get(Entry, entry_id) is None


@pytest.mark.unit
class TestGetChronicleEndpoint:
    """Test suite for GET /api/chronicle endpoint."""

    def test_get_chronicle_success(self, client, sample_scribe, auth_headers, entry_factory):
        """Test successfully retrieving scribe's chronicle."""
        # Create multiple entries
        entry_factory(sample_scribe.id, content="First entry")
        entry_factory(sample_scribe.id, content="Second entry")
        entry_factory(sample_scribe.id, content="Third entry")

        response = client.get("/api/chronicle", headers=auth_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert "data" in data
        assert isinstance(data["data"], list)
        assert len(data["data"]) == 3

        # Verify entries are in correct order (newest first)
        contents = [entry["attributes"]["content"] for entry in data["data"]]
        assert "Third entry" in contents

    def test_get_chronicle_empty(self, client, auth_headers):
        """Test retrieving chronicle when scribe has no entries."""
        response = client.get("/api/chronicle", headers=auth_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert data["data"] == []

    def test_get_chronicle_no_auth(self, client):
        """Test retrieving chronicle without authentication returns 401."""
        response = client.get("/api/chronicle")

        assert response.status_code == 401
        data = response.get_json()
        assert data["errors"][0]["status"] == "401"

    def test_get_chronicle_invalid_credentials(self, client, sample_scribe):
        """Test retrieving chronicle with wrong credentials returns 401."""
        bad_creds = base64.b64encode(
            f"{sample_scribe.username}:wrongpassword".encode()
        ).decode("utf-8")
        headers = {"Authorization": f"Basic {bad_creds}"}

        response = client.get("/api/chronicle", headers=headers)

        assert response.status_code == 401

    def test_get_chronicle_includes_public_and_private(self, client, db, sample_scribe, auth_headers):
        """Test that chronicle includes both public and private entries."""
        public_entry = Entry(
            content="Public entry",
            scribe_id=sample_scribe.id,
            visibility="public"
        )
        private_entry = Entry(
            content="Private entry",
            scribe_id=sample_scribe.id,
            visibility="private"
        )
        db.session.add_all([public_entry, private_entry])
        db.session.commit()

        response = client.get("/api/chronicle", headers=auth_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert len(data["data"]) == 2

        # Verify both entries are present
        contents = [entry["attributes"]["content"] for entry in data["data"]]
        assert "Public entry" in contents
        assert "Private entry" in contents

    def test_get_chronicle_only_own_entries(self, client, db, scribe_factory, auth_headers):
        """Test that chronicle only returns authenticated scribe's entries."""
        # Create entries for another user
        other_user = scribe_factory()
        other_entry = Entry(
            content="Other user entry",
            scribe_id=other_user.id,
            visibility="public"
        )
        db.session.add(other_entry)
        db.session.commit()

        response = client.get("/api/chronicle", headers=auth_headers)

        assert response.status_code == 200
        data = response.get_json()

        # Should not include other user's entry
        contents = [entry["attributes"]["content"] for entry in data["data"]]
        assert "Other user entry" not in contents

    def test_get_chronicle_chronological_order(self, client, db, sample_scribe, auth_headers):
        """Test that chronicle returns entries in chronological order (newest first)."""
        from datetime import datetime, timedelta

        # Create entries with explicit created_at timestamps to ensure different timestamps
        base_time = datetime.utcnow()
        
        entry1 = Entry(content="First", scribe_id=sample_scribe.id, visibility="public")
        entry1.created_at = base_time
        db.session.add(entry1)
        db.session.commit()

        entry2 = Entry(content="Second", scribe_id=sample_scribe.id, visibility="public")
        entry2.created_at = base_time + timedelta(seconds=1)
        db.session.add(entry2)
        db.session.commit()

        entry3 = Entry(content="Third", scribe_id=sample_scribe.id, visibility="public")
        entry3.created_at = base_time + timedelta(seconds=2)
        db.session.add(entry3)
        db.session.commit()

        response = client.get("/api/chronicle", headers=auth_headers)

        assert response.status_code == 200
        data = response.get_json()

        # Verify order is newest first
        contents = [entry["attributes"]["content"] for entry in data["data"]]
        assert contents[0] == "Third"
        assert contents[1] == "Second"
        assert contents[2] == "First"

    def test_get_chronicle_jsonapi_format(self, client, sample_scribe, auth_headers, entry_factory):
        """Test that chronicle response follows JSON:API specification."""
        entry_factory(sample_scribe.id)

        response = client.get("/api/chronicle", headers=auth_headers)

        assert response.status_code == 200
        data = response.get_json()

        # Verify JSON:API structure
        assert "data" in data
        assert isinstance(data["data"], list)

        for entry in data["data"]:
            assert "type" in entry
            assert entry["type"] == "entries"
            assert "id" in entry
            assert isinstance(entry["id"], str)
            assert "attributes" in entry

            # Verify camelCase attribute names
            attributes = entry["attributes"]
            assert "createdAt" in attributes
            assert "updatedAt" in attributes
            assert "scribeId" in attributes
            assert "scribeUsername" in attributes
