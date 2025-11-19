"""Integration tests for chronicle behavior.

Tests chronicle ordering, filtering, and complex entry management scenarios
using realistic Faker-generated data.
"""

import pytest
from base64 import b64encode
import time


def create_scribe_with_auth(client, faker):
    """Helper to create a scribe, unlock (login), and return auth headers."""
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

    return scribe_id, auth_headers


@pytest.mark.integration
def test_chronicle_reverse_chronological_order(client, faker):
    """Test that chronicle returns entries in reverse chronological order (newest first)."""
    scribe_id, auth_headers = create_scribe_with_auth(client, faker)

    # Create entries with small delays to ensure different timestamps
    entry_contents = []
    for i in range(5):
        content = faker.paragraph()
        entry_contents.append(content)
        response = client.post(
            "/api/entries", json={"content": content}, headers=auth_headers
        )
        assert response.status_code == 201
        if i < 4:  # No delay after last entry
            time.sleep(0.05)

    # Get chronicle
    response = client.get("/api/chronicle", headers=auth_headers)
    assert response.status_code == 200
    chronicle = response.get_json()["data"]

    # Verify reverse chronological order (newest first)
    assert len(chronicle) == 5
    for i in range(len(chronicle) - 1):
        current_time = chronicle[i]["attributes"]["createdAt"]
        next_time = chronicle[i + 1]["attributes"]["createdAt"]
        assert current_time >= next_time

    # The most recent entry should be first
    assert chronicle[0]["attributes"]["content"] == entry_contents[-1]


@pytest.mark.integration
def test_chronicle_includes_both_public_and_private_entries(client, faker):
    """Test that chronicle includes both public and private entries for the owner."""
    scribe_id, auth_headers = create_scribe_with_auth(client, faker)

    # Create mix of public and private entries
    public_count = 0
    private_count = 0
    for i in range(10):
        visibility = "public" if i % 3 == 0 else "private"
        if visibility == "public":
            public_count += 1
        else:
            private_count += 1

        client.post(
            "/api/entries",
            json={"content": faker.paragraph(), "visibility": visibility},
            headers=auth_headers,
        )

    # Get chronicle
    response = client.get("/api/chronicle", headers=auth_headers)
    assert response.status_code == 200
    chronicle = response.get_json()["data"]

    # Should include all entries
    assert len(chronicle) == 10

    # Count visibility types in chronicle
    chronicle_public = sum(
        1 for e in chronicle if e["attributes"]["visibility"] == "public"
    )
    chronicle_private = sum(
        1 for e in chronicle if e["attributes"]["visibility"] == "private"
    )

    assert chronicle_public == public_count
    assert chronicle_private == private_count


@pytest.mark.integration
def test_chronicle_after_entry_deletions(client, faker):
    """Test that chronicle correctly reflects deletions."""
    scribe_id, auth_headers = create_scribe_with_auth(client, faker)

    # Create multiple entries
    entry_ids = []
    for _ in range(8):
        response = client.post(
            "/api/entries",
            json={"content": faker.paragraph()},
            headers=auth_headers,
        )
        entry_ids.append(response.get_json()["data"]["id"])

    # Verify initial chronicle
    response = client.get("/api/chronicle", headers=auth_headers)
    assert len(response.get_json()["data"]) == 8

    # Delete every other entry
    deleted_ids = []
    for i, entry_id in enumerate(entry_ids):
        if i % 2 == 0:
            client.delete(f"/api/entries/{entry_id}", headers=auth_headers)
            deleted_ids.append(entry_id)

    # Get chronicle after deletions
    response = client.get("/api/chronicle", headers=auth_headers)
    chronicle = response.get_json()["data"]
    assert len(chronicle) == 4

    # Verify deleted entries are not in chronicle
    chronicle_ids = [e["id"] for e in chronicle]
    for deleted_id in deleted_ids:
        assert deleted_id not in chronicle_ids


@pytest.mark.integration
def test_chronicle_after_entry_updates(client, faker):
    """Test that chronicle reflects updated entry content."""
    scribe_id, auth_headers = create_scribe_with_auth(client, faker)

    # Create entries
    entry_ids = []
    for _ in range(5):
        response = client.post(
            "/api/entries",
            json={"content": faker.paragraph()},
            headers=auth_headers,
        )
        entry_ids.append(response.get_json()["data"]["id"])

    # Update some entries
    updated_contents = {}
    for i in range(0, len(entry_ids), 2):  # Update entries 0, 2, 4
        new_content = faker.paragraph()
        updated_contents[entry_ids[i]] = new_content
        client.patch(
            f"/api/entries/{entry_ids[i]}",
            json={"content": new_content},
            headers=auth_headers,
        )

    # Get chronicle
    response = client.get("/api/chronicle", headers=auth_headers)
    chronicle = response.get_json()["data"]

    # Verify updated contents appear in chronicle
    for entry in chronicle:
        entry_id = entry["id"]
        if entry_id in updated_contents:
            assert entry["attributes"]["content"] == updated_contents[entry_id]


@pytest.mark.integration
def test_chronicle_visibility_changes_reflected(client, faker):
    """Test that visibility changes are reflected in chronicle."""
    scribe_id, auth_headers = create_scribe_with_auth(client, faker)

    # Create public entries
    entry_ids = []
    for _ in range(4):
        response = client.post(
            "/api/entries",
            json={"content": faker.paragraph(), "visibility": "public"},
            headers=auth_headers,
        )
        entry_ids.append(response.get_json()["data"]["id"])

    # Change some to private
    for i in range(0, len(entry_ids), 2):
        client.patch(
            f"/api/entries/{entry_ids[i]}",
            json={"visibility": "private"},
            headers=auth_headers,
        )

    # Get chronicle
    response = client.get("/api/chronicle", headers=auth_headers)
    chronicle = response.get_json()["data"]

    # Verify visibility in chronicle
    for entry in chronicle:
        entry_id = entry["id"]
        if entry_id in [entry_ids[0], entry_ids[2]]:
            assert entry["attributes"]["visibility"] == "private"
        else:
            assert entry["attributes"]["visibility"] == "public"


@pytest.mark.integration
def test_empty_chronicle_for_new_scribe(client, faker):
    """Test that newly created scribe has empty chronicle."""
    scribe_id, auth_headers = create_scribe_with_auth(client, faker)

    response = client.get("/api/chronicle", headers=auth_headers)
    assert response.status_code == 200
    assert response.get_json()["data"] == []


@pytest.mark.integration
def test_chronicle_with_varied_entry_lengths(client, faker):
    """Test chronicle with entries of varying content lengths."""
    scribe_id, auth_headers = create_scribe_with_auth(client, faker)

    # Create entries with different content lengths
    lengths = [
        faker.sentence(),  # Short
        faker.paragraph(),  # Medium
        faker.text(max_nb_chars=1000),  # Long
        faker.sentence(),  # Short again
        faker.text(max_nb_chars=500),  # Medium-long
    ]

    for content in lengths:
        response = client.post(
            "/api/entries", json={"content": content}, headers=auth_headers
        )
        assert response.status_code == 201

    # Get chronicle
    response = client.get("/api/chronicle", headers=auth_headers)
    chronicle = response.get_json()["data"]
    assert len(chronicle) == 5

    # Verify all content is properly returned
    chronicle_contents = [e["attributes"]["content"] for e in chronicle]
    for content in lengths:
        assert content in chronicle_contents


@pytest.mark.integration
def test_chronicle_ordering_after_multiple_operations(client, faker):
    """Test chronicle ordering after creating, updating, and deleting entries."""
    scribe_id, auth_headers = create_scribe_with_auth(client, faker)

    # Create initial entries
    entry_ids = []
    for _ in range(6):
        response = client.post(
            "/api/entries",
            json={"content": faker.paragraph()},
            headers=auth_headers,
        )
        entry_ids.append(response.get_json()["data"]["id"])
        time.sleep(0.05)

    # Delete middle entry
    client.delete(f"/api/entries/{entry_ids[2]}", headers=auth_headers)

    # Update an entry (should not change its position in chronicle)
    client.patch(
        f"/api/entries/{entry_ids[1]}",
        json={"content": faker.paragraph()},
        headers=auth_headers,
    )

    # Create new entry
    response = client.post(
        "/api/entries", json={"content": faker.paragraph()}, headers=auth_headers
    )
    new_entry_id = response.get_json()["data"]["id"]

    # Get chronicle
    response = client.get("/api/chronicle", headers=auth_headers)
    chronicle = response.get_json()["data"]

    # Should have 6 entries (6 created - 1 deleted + 1 new)
    assert len(chronicle) == 6

    # Newest entry should be first
    assert chronicle[0]["id"] == new_entry_id

    # Verify deleted entry is not present
    chronicle_ids = [e["id"] for e in chronicle]
    assert entry_ids[2] not in chronicle_ids

    # Verify chronological ordering
    for i in range(len(chronicle) - 1):
        current_time = chronicle[i]["attributes"]["createdAt"]
        next_time = chronicle[i + 1]["attributes"]["createdAt"]
        assert current_time >= next_time


@pytest.mark.integration
def test_chronicle_with_bulk_entries(client, faker):
    """Test chronicle performance with large number of entries."""
    scribe_id, auth_headers = create_scribe_with_auth(client, faker)

    # Create many entries
    num_entries = 50
    for _ in range(num_entries):
        client.post(
            "/api/entries",
            json={"content": faker.paragraph()},
            headers=auth_headers,
        )

    # Get chronicle
    response = client.get("/api/chronicle", headers=auth_headers)
    assert response.status_code == 200
    chronicle = response.get_json()["data"]
    assert len(chronicle) == num_entries

    # Verify ordering
    for i in range(len(chronicle) - 1):
        current_time = chronicle[i]["attributes"]["createdAt"]
        next_time = chronicle[i + 1]["attributes"]["createdAt"]
        assert current_time >= next_time


@pytest.mark.integration
def test_chronicle_entry_attributes_complete(client, faker):
    """Test that chronicle entries contain all required attributes."""
    scribe_id, auth_headers = create_scribe_with_auth(client, faker)

    # Create an entry
    content = faker.paragraph()
    response = client.post(
        "/api/entries",
        json={"content": content, "visibility": "private"},
        headers=auth_headers,
    )
    assert response.status_code == 201

    # Get chronicle
    response = client.get("/api/chronicle", headers=auth_headers)
    chronicle = response.get_json()["data"]
    assert len(chronicle) == 1

    entry = chronicle[0]

    # Verify JSON:API structure
    assert "type" in entry
    assert entry["type"] == "entries"
    assert "id" in entry
    assert "attributes" in entry

    # Verify all required attributes
    attrs = entry["attributes"]
    assert "content" in attrs
    assert attrs["content"] == content
    assert "visibility" in attrs
    assert attrs["visibility"] == "private"
    assert "createdAt" in attrs
    assert "updatedAt" in attrs
    assert "scribeId" in attrs
    assert attrs["scribeId"] == int(scribe_id)
    assert "scribeUsername" in attrs

    # Verify timestamp format (ISO 8601 with Z)
    assert attrs["createdAt"].endswith("Z") or "+" in attrs["createdAt"]
    assert attrs["updatedAt"].endswith("Z") or "+" in attrs["updatedAt"]


@pytest.mark.integration
def test_chronicle_after_clearing_all_entries(client, faker):
    """Test chronicle after creating and then deleting all entries."""
    scribe_id, auth_headers = create_scribe_with_auth(client, faker)

    # Create entries
    entry_ids = []
    for _ in range(5):
        response = client.post(
            "/api/entries",
            json={"content": faker.paragraph()},
            headers=auth_headers,
        )
        entry_ids.append(response.get_json()["data"]["id"])

    # Verify chronicle has entries
    response = client.get("/api/chronicle", headers=auth_headers)
    assert len(response.get_json()["data"]) == 5

    # Delete all entries
    for entry_id in entry_ids:
        client.delete(f"/api/entries/{entry_id}", headers=auth_headers)

    # Chronicle should be empty
    response = client.get("/api/chronicle", headers=auth_headers)
    assert response.status_code == 200
    assert response.get_json()["data"] == []


@pytest.mark.integration
def test_chronicle_preserves_entry_order_across_requests(client, faker):
    """Test that chronicle order is consistent across multiple requests."""
    scribe_id, auth_headers = create_scribe_with_auth(client, faker)

    # Create entries
    for _ in range(10):
        client.post(
            "/api/entries",
            json={"content": faker.paragraph()},
            headers=auth_headers,
        )

    # Get chronicle multiple times
    first_response = client.get("/api/chronicle", headers=auth_headers)
    first_chronicle = first_response.get_json()["data"]

    second_response = client.get("/api/chronicle", headers=auth_headers)
    second_chronicle = second_response.get_json()["data"]

    third_response = client.get("/api/chronicle", headers=auth_headers)
    third_chronicle = third_response.get_json()["data"]

    # Verify order is consistent
    first_ids = [e["id"] for e in first_chronicle]
    second_ids = [e["id"] for e in second_chronicle]
    third_ids = [e["id"] for e in third_chronicle]

    assert first_ids == second_ids == third_ids
