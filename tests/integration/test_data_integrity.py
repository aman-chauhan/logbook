"""Integration tests for data integrity.

Tests cascade deletes, database consistency, concurrent operations,
and transaction handling using realistic Faker-generated data.
"""

import pytest
from base64 import b64encode


def create_scribe_with_entries(client, faker, num_entries=5):
    """Helper to create a scribe, unlock (login), and create entries."""
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

    # Create entries
    entry_ids = []
    for _ in range(num_entries):
        response = client.post(
            "/api/entries",
            json={"content": faker.paragraph()},
            headers=auth_headers,
        )
        entry_ids.append(response.get_json()["data"]["id"])

    return {
        "id": scribe_id,
        "username": username,
        "email": email,
        "password": password,
        "auth_headers": auth_headers,
        "entry_ids": entry_ids,
    }


@pytest.mark.integration
def test_cascade_delete_scribe_removes_all_entries(client, faker):
    """Test that deleting a scribe cascades to delete all their entries."""
    # Create scribe with multiple entries
    scribe = create_scribe_with_entries(client, faker, num_entries=10)

    # Verify entries exist
    for entry_id in scribe["entry_ids"]:
        response = client.get(f"/api/entries/{entry_id}")
        assert response.status_code == 200

    # Delete scribe
    response = client.delete(
        f"/api/scribes/{scribe['id']}", headers=scribe["auth_headers"]
    )
    assert response.status_code == 204

    # Verify all entries are deleted
    for entry_id in scribe["entry_ids"]:
        response = client.get(f"/api/entries/{entry_id}")
        assert response.status_code == 404

    # Verify scribe is deleted
    response = client.get(f"/api/scribes/{scribe['id']}")
    assert response.status_code == 404


@pytest.mark.integration
def test_cascade_delete_with_mixed_visibility_entries(client, faker):
    """Test cascade delete works with both public and private entries."""
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

    # Create mix of public and private entries
    entry_ids = []
    for i in range(8):
        visibility = "public" if i % 2 == 0 else "private"
        response = client.post(
            "/api/entries",
            json={"content": faker.paragraph(), "visibility": visibility},
            headers=auth_headers,
        )
        entry_ids.append(response.get_json()["data"]["id"])

    # Delete scribe
    client.delete(f"/api/scribes/{scribe_id}", headers=auth_headers)

    # Verify all entries are deleted regardless of visibility
    for entry_id in entry_ids:
        response = client.get(f"/api/entries/{entry_id}")
        assert response.status_code == 404


@pytest.mark.integration
def test_entry_references_after_scribe_profile_updates(client, faker):
    """Test that entries remain valid after scribe profile updates."""
    # Create scribe with entries
    scribe = create_scribe_with_entries(client, faker, num_entries=5)
    original_username = scribe["username"]

    # Update scribe profile
    new_email = faker.email()
    new_bio = faker.text(max_nb_chars=200)
    response = client.patch(
        f"/api/scribes/{scribe['id']}",
        json={"email": new_email, "bio": new_bio},
        headers=scribe["auth_headers"],
    )
    assert response.status_code == 200

    # Verify all entries still exist and reference correct scribe
    for entry_id in scribe["entry_ids"]:
        response = client.get(f"/api/entries/{entry_id}")
        assert response.status_code == 200
        entry_data = response.get_json()["data"]["attributes"]
        assert entry_data["scribeId"] == scribe["id"]
        assert entry_data["scribeUsername"] == original_username


@pytest.mark.integration
def test_entry_count_consistency_across_operations(client, faker):
    """Test that entry counts remain consistent through various operations."""
    scribe = create_scribe_with_entries(client, faker, num_entries=0)

    # Track expected count
    expected_count = 0

    # Create entries
    for _ in range(5):
        client.post(
            "/api/entries",
            json={"content": faker.paragraph()},
            headers=scribe["auth_headers"],
        )
        expected_count += 1

    # Verify count
    response = client.get("/api/chronicle", headers=scribe["auth_headers"])
    assert len(response.get_json()["data"]) == expected_count

    # Create more entries
    entry_ids = []
    for _ in range(3):
        response = client.post(
            "/api/entries",
            json={"content": faker.paragraph()},
            headers=scribe["auth_headers"],
        )
        entry_ids.append(response.get_json()["data"]["id"])
        expected_count += 1

    # Verify count
    response = client.get("/api/chronicle", headers=scribe["auth_headers"])
    assert len(response.get_json()["data"]) == expected_count

    # Delete some entries
    for entry_id in entry_ids[:2]:
        client.delete(f"/api/entries/{entry_id}", headers=scribe["auth_headers"])
        expected_count -= 1

    # Verify count
    response = client.get("/api/chronicle", headers=scribe["auth_headers"])
    assert len(response.get_json()["data"]) == expected_count

    # Final verification
    assert expected_count == 6  # 5 + 3 - 2


@pytest.mark.integration
def test_database_consistency_after_failed_operations(client, faker):
    """Test that database remains consistent after failed operations."""
    scribe = create_scribe_with_entries(client, faker, num_entries=3)

    # Get initial state
    initial_response = client.get("/api/chronicle", headers=scribe["auth_headers"])
    initial_count = len(initial_response.get_json()["data"])
    initial_profile = client.get(f"/api/scribes/{scribe['id']}").get_json()

    # Try to update with duplicate email (should fail)
    other_scribe = create_scribe_with_entries(client, faker, num_entries=0)
    response = client.patch(
        f"/api/scribes/{scribe['id']}",
        json={"email": other_scribe["email"]},
        headers=scribe["auth_headers"],
    )
    assert response.status_code == 409

    # Verify scribe profile unchanged
    current_profile = client.get(f"/api/scribes/{scribe['id']}").get_json()
    assert (
        current_profile["data"]["attributes"]["email"]
        == initial_profile["data"]["attributes"]["email"]
    )

    # Try to update nonexistent entry (should fail)
    fake_uuid = "00000000-0000-0000-0000-000000000000"
    response = client.patch(
        f"/api/entries/{fake_uuid}",
        json={"content": faker.paragraph()},
        headers=scribe["auth_headers"],
    )
    assert response.status_code == 404

    # Verify chronicle unchanged
    current_response = client.get("/api/chronicle", headers=scribe["auth_headers"])
    current_count = len(current_response.get_json()["data"])
    assert current_count == initial_count


@pytest.mark.integration
def test_concurrent_entry_creation_by_same_user(client, faker):
    """Test data consistency with rapid entry creation."""
    scribe = create_scribe_with_entries(client, faker, num_entries=0)

    # Rapidly create multiple entries
    num_entries = 20
    for _ in range(num_entries):
        response = client.post(
            "/api/entries",
            json={"content": faker.paragraph()},
            headers=scribe["auth_headers"],
        )
        assert response.status_code == 201

    # Verify all entries exist in chronicle
    response = client.get("/api/chronicle", headers=scribe["auth_headers"])
    chronicle = response.get_json()["data"]
    assert len(chronicle) == num_entries

    # Verify all entries are unique
    entry_ids = [e["id"] for e in chronicle]
    assert len(entry_ids) == len(set(entry_ids))


@pytest.mark.integration
def test_referential_integrity_scribe_to_entries(client, faker):
    """Test that entry.scribe_id always references valid scribe."""
    # Create scribe with entries
    scribe = create_scribe_with_entries(client, faker, num_entries=5)

    # Verify all entries reference the correct scribe
    for entry_id in scribe["entry_ids"]:
        response = client.get(f"/api/entries/{entry_id}")
        assert response.status_code == 200
        assert response.get_json()["data"]["attributes"]["scribeId"] == scribe["id"]

    # After scribe deletion, entries should be gone (cascade)
    client.delete(f"/api/scribes/{scribe['id']}", headers=scribe["auth_headers"])

    for entry_id in scribe["entry_ids"]:
        response = client.get(f"/api/entries/{entry_id}")
        assert response.status_code == 404


@pytest.mark.integration
def test_timestamp_consistency_on_updates(client, faker):
    """Test that updated_at changes but created_at remains constant."""
    import time

    scribe = create_scribe_with_entries(client, faker, num_entries=1)
    entry_id = scribe["entry_ids"][0]

    # Get initial timestamps
    response = client.get(f"/api/entries/{entry_id}")
    initial_data = response.get_json()["data"]["attributes"]
    created_at = initial_data["createdAt"]
    updated_at_1 = initial_data["updatedAt"]

    # Wait and update
    time.sleep(0.1)
    client.patch(
        f"/api/entries/{entry_id}",
        json={"content": faker.paragraph()},
        headers=scribe["auth_headers"],
    )

    # Get updated timestamps
    response = client.get(f"/api/entries/{entry_id}")
    updated_data = response.get_json()["data"]["attributes"]
    updated_at_2 = updated_data["updatedAt"]

    # created_at should not change
    assert updated_data["createdAt"] == created_at

    # updated_at should change
    assert updated_at_2 > updated_at_1


@pytest.mark.integration
def test_unique_constraint_enforcement_username(client, faker):
    """Test that username uniqueness is enforced at database level."""
    username = faker.user_name()

    # Create first scribe
    response = client.post(
        "/api/auth/enlist",
        json={
            "username": username,
            "email": faker.email(),
            "password": faker.password(length=12),
        },
    )
    assert response.status_code == 201

    # Attempt to create second scribe with same username
    response = client.post(
        "/api/auth/enlist",
        json={
            "username": username,
            "email": faker.email(),
            "password": faker.password(length=12),
        },
    )
    assert response.status_code == 409
    assert "errors" in response.get_json()


@pytest.mark.integration
def test_unique_constraint_enforcement_email(client, faker):
    """Test that email uniqueness is enforced at database level."""
    email = faker.email()

    # Create first scribe
    response = client.post(
        "/api/auth/enlist",
        json={
            "username": faker.user_name(),
            "email": email,
            "password": faker.password(length=12),
        },
    )
    assert response.status_code == 201

    # Attempt to create second scribe with same email
    response = client.post(
        "/api/auth/enlist",
        json={
            "username": faker.user_name(),
            "email": email,
            "password": faker.password(length=12),
        },
    )
    assert response.status_code == 409
    assert "errors" in response.get_json()


@pytest.mark.integration
def test_bulk_operations_maintain_consistency(client, faker):
    """Test data consistency with bulk create, update, delete operations."""
    scribe = create_scribe_with_entries(client, faker, num_entries=0)

    # Bulk create
    entry_ids = []
    for _ in range(30):
        response = client.post(
            "/api/entries",
            json={"content": faker.paragraph()},
            headers=scribe["auth_headers"],
        )
        entry_ids.append(response.get_json()["data"]["id"])

    # Verify count
    response = client.get("/api/chronicle", headers=scribe["auth_headers"])
    assert len(response.get_json()["data"]) == 30

    # Bulk update (update every entry)
    for entry_id in entry_ids:
        response = client.patch(
            f"/api/entries/{entry_id}",
            json={"content": faker.paragraph()},
            headers=scribe["auth_headers"],
        )
        assert response.status_code == 200

    # Verify count unchanged
    response = client.get("/api/chronicle", headers=scribe["auth_headers"])
    assert len(response.get_json()["data"]) == 30

    # Bulk delete (delete half)
    for entry_id in entry_ids[:15]:
        response = client.delete(
            f"/api/entries/{entry_id}", headers=scribe["auth_headers"]
        )
        assert response.status_code == 204

    # Verify count updated correctly
    response = client.get("/api/chronicle", headers=scribe["auth_headers"])
    assert len(response.get_json()["data"]) == 15

    # Verify correct entries remain
    remaining_chronicle = response.get_json()["data"]
    remaining_ids = [e["id"] for e in remaining_chronicle]
    for entry_id in entry_ids[15:]:
        assert entry_id in remaining_ids
    for entry_id in entry_ids[:15]:
        assert entry_id not in remaining_ids


@pytest.mark.integration
def test_data_isolation_between_scribes(client, faker):
    """Test that scribe data is properly isolated in database."""
    # Create three scribes with entries
    scribe_a = create_scribe_with_entries(client, faker, num_entries=5)
    scribe_b = create_scribe_with_entries(client, faker, num_entries=7)
    scribe_c = create_scribe_with_entries(client, faker, num_entries=3)

    # Delete scribe B
    client.delete(f"/api/scribes/{scribe_b['id']}", headers=scribe_b["auth_headers"])

    # Verify scribe A's data intact
    for entry_id in scribe_a["entry_ids"]:
        response = client.get(f"/api/entries/{entry_id}")
        assert response.status_code == 200

    response = client.get("/api/chronicle", headers=scribe_a["auth_headers"])
    assert len(response.get_json()["data"]) == 5

    # Verify scribe C's data intact
    for entry_id in scribe_c["entry_ids"]:
        response = client.get(f"/api/entries/{entry_id}")
        assert response.status_code == 200

    response = client.get("/api/chronicle", headers=scribe_c["auth_headers"])
    assert len(response.get_json()["data"]) == 3

    # Verify scribe B's entries are gone
    for entry_id in scribe_b["entry_ids"]:
        response = client.get(f"/api/entries/{entry_id}")
        assert response.status_code == 404


@pytest.mark.integration
def test_entry_visibility_consistency(client, faker):
    """Test that visibility settings are consistently enforced."""
    scribe = create_scribe_with_entries(client, faker, num_entries=0)
    other_scribe = create_scribe_with_entries(client, faker, num_entries=0)

    # Create entries with specific visibility
    public_entry = client.post(
        "/api/entries",
        json={"content": faker.paragraph(), "visibility": "public"},
        headers=scribe["auth_headers"],
    ).get_json()["data"]["id"]

    private_entry = client.post(
        "/api/entries",
        json={"content": faker.paragraph(), "visibility": "private"},
        headers=scribe["auth_headers"],
    ).get_json()["data"]["id"]

    # Public entry visible to others
    response = client.get(f"/api/entries/{public_entry}", headers=other_scribe["auth_headers"])
    assert response.status_code == 200

    # Private entry not visible to others
    response = client.get(f"/api/entries/{private_entry}", headers=other_scribe["auth_headers"])
    assert response.status_code == 404

    # Change public to private
    client.patch(
        f"/api/entries/{public_entry}",
        json={"visibility": "private"},
        headers=scribe["auth_headers"],
    )

    # Now not visible to others
    response = client.get(f"/api/entries/{public_entry}", headers=other_scribe["auth_headers"])
    assert response.status_code == 404

    # Change private to public
    client.patch(
        f"/api/entries/{private_entry}",
        json={"visibility": "public"},
        headers=scribe["auth_headers"],
    )

    # Now visible to others
    response = client.get(f"/api/entries/{private_entry}", headers=other_scribe["auth_headers"])
    assert response.status_code == 200
