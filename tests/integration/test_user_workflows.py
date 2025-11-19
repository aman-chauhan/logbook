"""Integration tests for complete user workflows.

Tests end-to-end user journeys from registration through deletion,
using realistic Faker-generated data.
"""

import pytest
from base64 import b64encode


@pytest.mark.integration
def test_complete_user_lifecycle(client, faker):
    """Test complete user journey: enlist -> create entries -> update profile -> delete account."""
    # Step 1: Enlist a new scribe
    username = faker.user_name()
    email = faker.email()
    password = faker.password(length=12)
    bio = faker.text(max_nb_chars=200)

    response = client.post(
        "/api/auth/enlist",
        json={"username": username, "email": email, "password": password},
    )
    assert response.status_code == 201
    data = response.get_json()
    scribe_id = data["data"]["id"]
    assert data["data"]["attributes"]["username"] == username
    assert data["data"]["attributes"]["email"] == email

    # Step 2: Unlock (login)
    auth_headers = {
        "Authorization": f'Basic {b64encode(f"{username}:{password}".encode()).decode()}'
    }
    response = client.post("/api/auth/unlock", headers=auth_headers)
    assert response.status_code == 200

    # Step 3: Create several entries
    entry_ids = []
    for i in range(3):
        entry_content = faker.paragraph()
        visibility = "public" if i % 2 == 0 else "private"
        response = client.post(
            "/api/entries",
            json={"content": entry_content, "visibility": visibility},
            headers=auth_headers,
        )
        assert response.status_code == 201
        entry_ids.append(response.get_json()["data"]["id"])

    # Step 4: Update profile
    new_bio = faker.text(max_nb_chars=150)
    response = client.patch(
        f"/api/scribes/{scribe_id}",
        json={"bio": new_bio},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.get_json()["data"]["attributes"]["bio"] == new_bio

    # Step 5: Verify chronicle contains all entries
    response = client.get("/api/chronicle", headers=auth_headers)
    assert response.status_code == 200
    chronicle = response.get_json()["data"]
    assert len(chronicle) == 3

    # Step 6: Delete account
    response = client.delete(f"/api/scribes/{scribe_id}", headers=auth_headers)
    assert response.status_code == 204

    # Step 7: Verify scribe is deleted
    response = client.get(f"/api/scribes/{scribe_id}")
    assert response.status_code == 404

    # Step 8: Verify entries are cascade deleted
    for entry_id in entry_ids:
        response = client.get(f"/api/entries/{entry_id}")
        assert response.status_code == 404


@pytest.mark.integration
def test_profile_updates_with_active_entries(client, faker):
    """Test that profile updates work correctly when scribe has active entries."""
    # Enlist scribe
    username = faker.user_name()
    email = faker.email()
    password = faker.password(length=12)

    response = client.post(
        "/api/auth/enlist",
        json={"username": username, "email": email, "password": password},
    )
    scribe_id = response.get_json()["data"]["id"]
    auth_headers = {
        "Authorization": f'Basic {b64encode(f"{username}:{password}".encode()).decode()}'
    }

    # Unlock (login)
    response = client.post("/api/auth/unlock", headers=auth_headers)
    assert response.status_code == 200

    # Create multiple entries
    entry_contents = [faker.paragraph() for _ in range(5)]
    for content in entry_contents:
        client.post(
            "/api/entries", json={"content": content}, headers=auth_headers
        )

    # Update email
    new_email = faker.email()
    response = client.patch(
        f"/api/scribes/{scribe_id}",
        json={"email": new_email},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.get_json()["data"]["attributes"]["email"] == new_email

    # Verify entries still accessible with old username but need new email for auth
    response = client.get("/api/chronicle", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.get_json()["data"]) == 5


@pytest.mark.integration
def test_password_change_workflow(client, faker):
    """Test changing password and continuing to use the account."""
    # Enlist scribe
    username = faker.user_name()
    email = faker.email()
    old_password = faker.password(length=12)

    response = client.post(
        "/api/auth/enlist",
        json={"username": username, "email": email, "password": old_password},
    )
    scribe_id = response.get_json()["data"]["id"]
    old_auth_headers = {
        "Authorization": f'Basic {b64encode(f"{username}:{old_password}".encode()).decode()}'
    }

    # Create entry with old password
    response = client.post(
        "/api/entries",
        json={"content": faker.paragraph()},
        headers=old_auth_headers,
    )
    assert response.status_code == 201

    # Change password
    new_password = faker.password(length=12)
    response = client.patch(
        f"/api/scribes/{scribe_id}",
        json={"password": new_password},
        headers=old_auth_headers,
    )
    assert response.status_code == 200

    # Old password should no longer work
    response = client.get("/api/chronicle", headers=old_auth_headers)
    assert response.status_code == 401

    # New password should work
    new_auth_headers = {
        "Authorization": f'Basic {b64encode(f"{username}:{new_password}".encode()).decode()}'
    }
    response = client.get("/api/chronicle", headers=new_auth_headers)
    assert response.status_code == 200
    assert len(response.get_json()["data"]) == 1


@pytest.mark.integration
def test_enlist_unlock_create_lock_unlock_cycle(client, faker):
    """Test the complete auth cycle: enlist -> unlock -> create -> lock -> unlock."""
    # Enlist
    username = faker.user_name()
    email = faker.email()
    password = faker.password(length=12)

    response = client.post(
        "/api/auth/enlist",
        json={"username": username, "email": email, "password": password},
    )
    assert response.status_code == 201
    scribe_id = response.get_json()["data"]["id"]

    # Unlock (verify credentials)
    auth_headers = {
        "Authorization": f'Basic {b64encode(f"{username}:{password}".encode()).decode()}'
    }
    response = client.post("/api/auth/unlock", headers=auth_headers)
    assert response.status_code == 200
    assert response.get_json()["data"]["id"] == scribe_id

    # Create entry
    entry_content = faker.paragraph()
    response = client.post(
        "/api/entries", json={"content": entry_content}, headers=auth_headers
    )
    assert response.status_code == 201
    entry_id = response.get_json()["data"]["id"]

    # Lock (informational, stateless)
    response = client.post("/api/auth/lock", headers=auth_headers)
    assert response.status_code == 204

    # Unlock again (should still work, API is stateless)
    response = client.post("/api/auth/unlock", headers=auth_headers)
    assert response.status_code == 200

    # Verify entry still exists and accessible
    response = client.get(f"/api/entries/{entry_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.get_json()["data"]["attributes"]["content"] == entry_content


@pytest.mark.integration
def test_multiple_profile_updates_in_sequence(client, faker):
    """Test updating multiple profile fields in sequence."""
    # Enlist
    username = faker.user_name()
    email = faker.email()
    password = faker.password(length=12)

    response = client.post(
        "/api/auth/enlist",
        json={"username": username, "email": email, "password": password},
    )
    scribe_id = response.get_json()["data"]["id"]
    auth_headers = {
        "Authorization": f'Basic {b64encode(f"{username}:{password}".encode()).decode()}'
    }

    # Unlock (login)
    response = client.post("/api/auth/unlock", headers=auth_headers)
    assert response.status_code == 200

    # Update bio
    new_bio = faker.text(max_nb_chars=200)
    response = client.patch(
        f"/api/scribes/{scribe_id}", json={"bio": new_bio}, headers=auth_headers
    )
    assert response.status_code == 200
    assert response.get_json()["data"]["attributes"]["bio"] == new_bio

    # Update email
    new_email = faker.email()
    response = client.patch(
        f"/api/scribes/{scribe_id}",
        json={"email": new_email},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.get_json()["data"]["attributes"]
    assert data["email"] == new_email
    assert data["bio"] == new_bio  # Bio should still be there

    # Update bio again
    newer_bio = faker.text(max_nb_chars=150)
    response = client.patch(
        f"/api/scribes/{scribe_id}",
        json={"bio": newer_bio},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.get_json()["data"]["attributes"]
    assert data["bio"] == newer_bio
    assert data["email"] == new_email  # Email should still be the new one


@pytest.mark.integration
def test_create_update_delete_entry_workflow(client, faker):
    """Test complete entry lifecycle: create -> update -> delete."""
    # Enlist scribe
    username = faker.user_name()
    email = faker.email()
    password = faker.password(length=12)

    response = client.post(
        "/api/auth/enlist",
        json={"username": username, "email": email, "password": password},
    )
    auth_headers = {
        "Authorization": f'Basic {b64encode(f"{username}:{password}".encode()).decode()}'
    }

    # Unlock (login)
    response = client.post("/api/auth/unlock", headers=auth_headers)
    assert response.status_code == 200

    # Create entry
    original_content = faker.paragraph()
    response = client.post(
        "/api/entries",
        json={"content": original_content, "visibility": "public"},
        headers=auth_headers,
    )
    assert response.status_code == 201
    entry_id = response.get_json()["data"]["id"]

    # Verify in chronicle
    response = client.get("/api/chronicle", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.get_json()["data"]) == 1

    # Update entry content
    updated_content = faker.paragraph()
    response = client.patch(
        f"/api/entries/{entry_id}",
        json={"content": updated_content},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.get_json()["data"]["attributes"]["content"] == updated_content

    # Update visibility
    response = client.patch(
        f"/api/entries/{entry_id}",
        json={"visibility": "private"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.get_json()["data"]["attributes"]["visibility"] == "private"

    # Delete entry
    response = client.delete(f"/api/entries/{entry_id}", headers=auth_headers)
    assert response.status_code == 204

    # Verify removed from chronicle
    response = client.get("/api/chronicle", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.get_json()["data"]) == 0

    # Verify entry no longer accessible
    response = client.get(f"/api/entries/{entry_id}")
    assert response.status_code == 404


@pytest.mark.integration
def test_bulk_entry_creation_and_chronicle_access(client, faker):
    """Test creating many entries and accessing them via chronicle."""
    # Enlist scribe
    username = faker.user_name()
    email = faker.email()
    password = faker.password(length=12)

    response = client.post(
        "/api/auth/enlist",
        json={"username": username, "email": email, "password": password},
    )
    auth_headers = {
        "Authorization": f'Basic {b64encode(f"{username}:{password}".encode()).decode()}'
    }

    # Unlock (login)
    response = client.post("/api/auth/unlock", headers=auth_headers)
    assert response.status_code == 200

    # Create 20 entries with varied content
    num_entries = 20
    for i in range(num_entries):
        content = faker.paragraph() if i % 2 == 0 else faker.text(max_nb_chars=500)
        visibility = "public" if i % 3 == 0 else "private"
        response = client.post(
            "/api/entries",
            json={"content": content, "visibility": visibility},
            headers=auth_headers,
        )
        assert response.status_code == 201

    # Access chronicle
    response = client.get("/api/chronicle", headers=auth_headers)
    assert response.status_code == 200
    chronicle = response.get_json()["data"]
    assert len(chronicle) == num_entries

    # Verify entries are in reverse chronological order
    for i in range(len(chronicle) - 1):
        current_time = chronicle[i]["attributes"]["createdAt"]
        next_time = chronicle[i + 1]["attributes"]["createdAt"]
        assert current_time >= next_time


@pytest.mark.integration
def test_profile_view_public_access(client, faker):
    """Test that scribe profiles are publicly viewable without authentication."""
    # Enlist scribe
    username = faker.user_name()
    email = faker.email()
    password = faker.password(length=12)
    bio = faker.text(max_nb_chars=200)

    response = client.post(
        "/api/auth/enlist",
        json={"username": username, "email": email, "password": password},
    )
    scribe_id = response.get_json()["data"]["id"]

    # Unlock (login) and update bio
    auth_headers = {
        "Authorization": f'Basic {b64encode(f"{username}:{password}".encode()).decode()}'
    }
    response = client.post("/api/auth/unlock", headers=auth_headers)
    assert response.status_code == 200

    client.patch(
        f"/api/scribes/{scribe_id}", json={"bio": bio}, headers=auth_headers
    )

    # Access profile without authentication
    response = client.get(f"/api/scribes/{scribe_id}")
    assert response.status_code == 200
    data = response.get_json()["data"]["attributes"]
    assert data["username"] == username
    assert data["email"] == email
    assert data["bio"] == bio


@pytest.mark.integration
def test_account_deletion_after_multiple_operations(client, faker):
    """Test account deletion after various profile and entry operations."""
    # Enlist scribe
    username = faker.user_name()
    email = faker.email()
    password = faker.password(length=12)

    response = client.post(
        "/api/auth/enlist",
        json={"username": username, "email": email, "password": password},
    )
    scribe_id = response.get_json()["data"]["id"]
    auth_headers = {
        "Authorization": f'Basic {b64encode(f"{username}:{password}".encode()).decode()}'
    }

    # Unlock (login)
    response = client.post("/api/auth/unlock", headers=auth_headers)
    assert response.status_code == 200

    # Update profile multiple times
    for _ in range(3):
        client.patch(
            f"/api/scribes/{scribe_id}",
            json={"bio": faker.text(max_nb_chars=100)},
            headers=auth_headers,
        )

    # Create and delete some entries
    entry_ids_to_keep = []
    for i in range(10):
        response = client.post(
            "/api/entries",
            json={"content": faker.paragraph()},
            headers=auth_headers,
        )
        entry_id = response.get_json()["data"]["id"]
        if i < 5:
            client.delete(f"/api/entries/{entry_id}", headers=auth_headers)
        else:
            entry_ids_to_keep.append(entry_id)

    # Verify chronicle has remaining entries
    response = client.get("/api/chronicle", headers=auth_headers)
    assert len(response.get_json()["data"]) == 5

    # Delete account
    response = client.delete(f"/api/scribes/{scribe_id}", headers=auth_headers)
    assert response.status_code == 204

    # Verify all remaining entries are deleted
    for entry_id in entry_ids_to_keep:
        response = client.get(f"/api/entries/{entry_id}")
        assert response.status_code == 404


@pytest.mark.integration
def test_attempted_unlock_after_deletion(client, faker):
    """Test that authentication fails after account deletion."""
    # Enlist scribe
    username = faker.user_name()
    email = faker.email()
    password = faker.password(length=12)

    response = client.post(
        "/api/auth/enlist",
        json={"username": username, "email": email, "password": password},
    )
    scribe_id = response.get_json()["data"]["id"]
    auth_headers = {
        "Authorization": f'Basic {b64encode(f"{username}:{password}".encode()).decode()}'
    }

    # Verify unlock works before deletion
    response = client.post("/api/auth/unlock", headers=auth_headers)
    assert response.status_code == 200

    # Delete account
    client.delete(f"/api/scribes/{scribe_id}", headers=auth_headers)

    # Attempt unlock after deletion
    response = client.post("/api/auth/unlock", headers=auth_headers)
    assert response.status_code == 401
    assert "errors" in response.get_json()


@pytest.mark.integration
def test_empty_chronicle_for_new_user(client, faker):
    """Test that newly enlisted users have an empty chronicle."""
    # Enlist scribe
    username = faker.user_name()
    email = faker.email()
    password = faker.password(length=12)

    response = client.post(
        "/api/auth/enlist",
        json={"username": username, "email": email, "password": password},
    )
    auth_headers = {
        "Authorization": f'Basic {b64encode(f"{username}:{password}".encode()).decode()}'
    }

    # Unlock (login)
    response = client.post("/api/auth/unlock", headers=auth_headers)
    assert response.status_code == 200

    # Check chronicle
    response = client.get("/api/chronicle", headers=auth_headers)
    assert response.status_code == 200
    assert response.get_json()["data"] == []


@pytest.mark.integration
def test_profile_and_entry_timestamps(client, faker):
    """Test that timestamps are properly maintained throughout workflows."""
    from datetime import datetime, timedelta

    # Enlist scribe
    username = faker.user_name()
    email = faker.email()
    password = faker.password(length=12)

    response = client.post(
        "/api/auth/enlist",
        json={"username": username, "email": email, "password": password},
    )
    scribe_id = response.get_json()["data"]["id"]
    scribe_data = response.get_json()["data"]["attributes"]
    created_at = scribe_data["createdAt"]
    updated_at = scribe_data["updatedAt"]

    # Parse timestamps and verify they're within 1 second (handles DB operation timing)
    created_dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
    updated_dt = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
    assert abs((created_dt - updated_dt).total_seconds()) < 1  # Should be nearly equal on creation

    auth_headers = {
        "Authorization": f'Basic {b64encode(f"{username}:{password}".encode()).decode()}'
    }

    # Unlock (login)
    response = client.post("/api/auth/unlock", headers=auth_headers)
    assert response.status_code == 200

    # Update profile and verify updatedAt changes
    import time
    time.sleep(0.1)  # Small delay to ensure timestamp difference
    response = client.patch(
        f"/api/scribes/{scribe_id}",
        json={"bio": faker.text(max_nb_chars=100)},
        headers=auth_headers,
    )
    new_updated_at = response.get_json()["data"]["attributes"]["updatedAt"]
    assert new_updated_at > created_at

    # Create entry and verify timestamps
    response = client.post(
        "/api/entries", json={"content": faker.paragraph()}, headers=auth_headers
    )
    entry_data = response.get_json()["data"]["attributes"]
    entry_created = entry_data["createdAt"]
    entry_updated = entry_data["updatedAt"]

    # Parse timestamps and verify they're within 1 second (handles DB operation timing)
    entry_created_dt = datetime.fromisoformat(entry_created.replace('Z', '+00:00'))
    entry_updated_dt = datetime.fromisoformat(entry_updated.replace('Z', '+00:00'))
    assert abs((entry_created_dt - entry_updated_dt).total_seconds()) < 1  # Should be nearly equal on creation
    assert entry_created[-1] == "Z"  # Should have UTC marker


@pytest.mark.integration
def test_email_uniqueness_across_lifecycle(client, faker):
    """Test that email uniqueness is enforced even after deletions."""
    email = faker.email()
    password = faker.password(length=12)

    # Enlist first scribe
    username1 = faker.user_name()
    response = client.post(
        "/api/auth/enlist",
        json={"username": username1, "email": email, "password": password},
    )
    assert response.status_code == 201
    scribe_id = response.get_json()["data"]["id"]

    # Try to enlist with same email
    username2 = faker.user_name()
    response = client.post(
        "/api/auth/enlist",
        json={"username": username2, "email": email, "password": password},
    )
    assert response.status_code == 409

    # Unlock and delete first scribe
    auth_headers = {
        "Authorization": f'Basic {b64encode(f"{username1}:{password}".encode()).decode()}'
    }
    response = client.post("/api/auth/unlock", headers=auth_headers)
    assert response.status_code == 200
    client.delete(f"/api/scribes/{scribe_id}", headers=auth_headers)

    # Now should be able to enlist with that email
    response = client.post(
        "/api/auth/enlist",
        json={"username": username2, "email": email, "password": password},
    )
    assert response.status_code == 201


@pytest.mark.integration
def test_username_uniqueness_across_lifecycle(client, faker):
    """Test that username uniqueness is enforced even after deletions."""
    username = faker.user_name()
    password = faker.password(length=12)

    # Enlist first scribe
    email1 = faker.email()
    response = client.post(
        "/api/auth/enlist",
        json={"username": username, "email": email1, "password": password},
    )
    assert response.status_code == 201
    scribe_id = response.get_json()["data"]["id"]

    # Try to enlist with same username
    email2 = faker.email()
    response = client.post(
        "/api/auth/enlist",
        json={"username": username, "email": email2, "password": password},
    )
    assert response.status_code == 409

    # Unlock and delete first scribe
    auth_headers = {
        "Authorization": f'Basic {b64encode(f"{username}:{password}".encode()).decode()}'
    }
    response = client.post("/api/auth/unlock", headers=auth_headers)
    assert response.status_code == 200
    client.delete(f"/api/scribes/{scribe_id}", headers=auth_headers)

    # Now should be able to enlist with that username
    response = client.post(
        "/api/auth/enlist",
        json={"username": username, "email": email2, "password": password},
    )
    assert response.status_code == 201
