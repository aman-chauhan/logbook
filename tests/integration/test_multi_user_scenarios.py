"""Integration tests for multi-user scenarios.

Tests interactions between multiple users, privacy boundaries,
and authorization checks using realistic Faker-generated data.
"""

import pytest
from base64 import b64encode


def create_scribe(client, faker):
    """Helper function to create a scribe and return credentials."""
    username = faker.user_name()
    email = faker.email()
    password = faker.password(length=12)
    bio = faker.text(max_nb_chars=200)

    response = client.post(
        "/api/auth/enlist",
        json={"username": username, "email": email, "password": password},
    )
    assert response.status_code == 201
    scribe_id = response.get_json()["data"]["id"]

    auth_headers = {
        "Authorization": f'Basic {b64encode(f"{username}:{password}".encode()).decode()}'
    }

    # Update bio
    client.patch(
        f"/api/scribes/{scribe_id}", json={"bio": bio}, headers=auth_headers
    )

    return {
        "id": scribe_id,
        "username": username,
        "email": email,
        "password": password,
        "bio": bio,
        "auth_headers": auth_headers,
    }


@pytest.mark.integration
def test_public_entry_visible_to_all_users(client, faker):
    """Test that public entries are visible to all users."""
    # Create two scribes
    scribe_a = create_scribe(client, faker)
    scribe_b = create_scribe(client, faker)

    # Scribe A creates a public entry
    entry_content = faker.paragraph()
    response = client.post(
        "/api/entries",
        json={"content": entry_content, "visibility": "public"},
        headers=scribe_a["auth_headers"],
    )
    assert response.status_code == 201
    entry_id = response.get_json()["data"]["id"]

    # Scribe B can view the public entry
    response = client.get(f"/api/entries/{entry_id}", headers=scribe_b["auth_headers"])
    assert response.status_code == 200
    assert response.get_json()["data"]["attributes"]["content"] == entry_content

    # Unauthenticated user can also view it
    response = client.get(f"/api/entries/{entry_id}")
    assert response.status_code == 200


@pytest.mark.integration
def test_private_entry_only_visible_to_owner(client, faker):
    """Test that private entries are only visible to the owner."""
    # Create two scribes
    scribe_a = create_scribe(client, faker)
    scribe_b = create_scribe(client, faker)

    # Scribe A creates a private entry
    entry_content = faker.paragraph()
    response = client.post(
        "/api/entries",
        json={"content": entry_content, "visibility": "private"},
        headers=scribe_a["auth_headers"],
    )
    assert response.status_code == 201
    entry_id = response.get_json()["data"]["id"]

    # Scribe A can view their own private entry
    response = client.get(f"/api/entries/{entry_id}", headers=scribe_a["auth_headers"])
    assert response.status_code == 200

    # Scribe B cannot view the private entry (returns 404 to hide existence)
    response = client.get(f"/api/entries/{entry_id}", headers=scribe_b["auth_headers"])
    assert response.status_code == 404

    # Unauthenticated user cannot view it either
    response = client.get(f"/api/entries/{entry_id}")
    assert response.status_code == 404


@pytest.mark.integration
def test_user_cannot_modify_another_users_entry(client, faker):
    """Test that users cannot update or delete entries they don't own."""
    # Create two scribes
    scribe_a = create_scribe(client, faker)
    scribe_b = create_scribe(client, faker)

    # Scribe A creates an entry
    response = client.post(
        "/api/entries",
        json={"content": faker.paragraph(), "visibility": "public"},
        headers=scribe_a["auth_headers"],
    )
    entry_id = response.get_json()["data"]["id"]

    # Scribe B attempts to update the entry
    response = client.patch(
        f"/api/entries/{entry_id}",
        json={"content": faker.paragraph()},
        headers=scribe_b["auth_headers"],
    )
    assert response.status_code == 403

    # Scribe B attempts to delete the entry
    response = client.delete(
        f"/api/entries/{entry_id}", headers=scribe_b["auth_headers"]
    )
    assert response.status_code == 403

    # Entry should still exist and be accessible
    response = client.get(f"/api/entries/{entry_id}")
    assert response.status_code == 200


@pytest.mark.integration
def test_user_cannot_modify_another_users_profile(client, faker):
    """Test that users cannot update or delete other users' profiles."""
    # Create two scribes
    scribe_a = create_scribe(client, faker)
    scribe_b = create_scribe(client, faker)

    # Scribe B attempts to update Scribe A's profile
    response = client.patch(
        f"/api/scribes/{scribe_a['id']}",
        json={"bio": faker.text(max_nb_chars=100)},
        headers=scribe_b["auth_headers"],
    )
    assert response.status_code == 403

    # Scribe B attempts to delete Scribe A's account
    response = client.delete(
        f"/api/scribes/{scribe_a['id']}", headers=scribe_b["auth_headers"]
    )
    assert response.status_code == 403

    # Scribe A's profile should still exist
    response = client.get(f"/api/scribes/{scribe_a['id']}")
    assert response.status_code == 200


@pytest.mark.integration
def test_multiple_users_with_separate_chronicles(client, faker):
    """Test that each user's chronicle only contains their own entries."""
    # Create three scribes
    scribe_a = create_scribe(client, faker)
    scribe_b = create_scribe(client, faker)
    scribe_c = create_scribe(client, faker)

    # Each scribe creates different numbers of entries
    for _ in range(5):
        client.post(
            "/api/entries",
            json={"content": faker.paragraph()},
            headers=scribe_a["auth_headers"],
        )

    for _ in range(3):
        client.post(
            "/api/entries",
            json={"content": faker.paragraph()},
            headers=scribe_b["auth_headers"],
        )

    for _ in range(7):
        client.post(
            "/api/entries",
            json={"content": faker.paragraph()},
            headers=scribe_c["auth_headers"],
        )

    # Verify each chronicle contains only own entries
    response = client.get("/api/chronicle", headers=scribe_a["auth_headers"])
    assert len(response.get_json()["data"]) == 5

    response = client.get("/api/chronicle", headers=scribe_b["auth_headers"])
    assert len(response.get_json()["data"]) == 3

    response = client.get("/api/chronicle", headers=scribe_c["auth_headers"])
    assert len(response.get_json()["data"]) == 7


@pytest.mark.integration
def test_all_user_profiles_publicly_viewable(client, faker):
    """Test that all users can view each other's profiles without authentication."""
    # Create multiple scribes with varied profiles
    scribes = [create_scribe(client, faker) for _ in range(5)]

    # Each scribe can view all other profiles
    for scribe in scribes:
        for other_scribe in scribes:
            response = client.get(f"/api/scribes/{other_scribe['id']}")
            assert response.status_code == 200
            data = response.get_json()["data"]["attributes"]
            assert data["username"] == other_scribe["username"]
            assert data["email"] == other_scribe["email"]
            assert data["bio"] == other_scribe["bio"]

    # Unauthenticated users can also view profiles
    for scribe in scribes:
        response = client.get(f"/api/scribes/{scribe['id']}")
        assert response.status_code == 200


@pytest.mark.integration
def test_mixed_visibility_entries_across_users(client, faker):
    """Test public/private entry visibility with multiple users."""
    # Create three scribes
    scribe_a = create_scribe(client, faker)
    scribe_b = create_scribe(client, faker)
    scribe_c = create_scribe(client, faker)

    # Scribe A creates mix of public and private entries
    public_entries = []
    private_entries = []
    for i in range(6):
        visibility = "public" if i % 2 == 0 else "private"
        response = client.post(
            "/api/entries",
            json={"content": faker.paragraph(), "visibility": visibility},
            headers=scribe_a["auth_headers"],
        )
        entry_id = response.get_json()["data"]["id"]
        if visibility == "public":
            public_entries.append(entry_id)
        else:
            private_entries.append(entry_id)

    # Scribe B can view public entries
    for entry_id in public_entries:
        response = client.get(f"/api/entries/{entry_id}", headers=scribe_b["auth_headers"])
        assert response.status_code == 200

    # Scribe B cannot view private entries
    for entry_id in private_entries:
        response = client.get(f"/api/entries/{entry_id}", headers=scribe_b["auth_headers"])
        assert response.status_code == 404

    # Scribe C (unauthenticated check) cannot view private entries
    for entry_id in private_entries:
        response = client.get(f"/api/entries/{entry_id}")
        assert response.status_code == 404

    # Scribe A can view all their own entries
    response = client.get("/api/chronicle", headers=scribe_a["auth_headers"])
    assert len(response.get_json()["data"]) == 6


@pytest.mark.integration
def test_user_deletion_does_not_affect_others(client, faker):
    """Test that deleting one user doesn't affect other users' data."""
    # Create three scribes
    scribe_a = create_scribe(client, faker)
    scribe_b = create_scribe(client, faker)
    scribe_c = create_scribe(client, faker)

    # All scribes create entries
    for scribe in [scribe_a, scribe_b, scribe_c]:
        for _ in range(3):
            client.post(
                "/api/entries",
                json={"content": faker.paragraph()},
                headers=scribe["auth_headers"],
            )

    # Delete Scribe B
    client.delete(f"/api/scribes/{scribe_b['id']}", headers=scribe_b["auth_headers"])

    # Scribe A still has their entries
    response = client.get("/api/chronicle", headers=scribe_a["auth_headers"])
    assert len(response.get_json()["data"]) == 3

    # Scribe C still has their entries
    response = client.get("/api/chronicle", headers=scribe_c["auth_headers"])
    assert len(response.get_json()["data"]) == 3

    # Scribe A and C can still view their profiles
    response = client.get(f"/api/scribes/{scribe_a['id']}")
    assert response.status_code == 200

    response = client.get(f"/api/scribes/{scribe_c['id']}")
    assert response.status_code == 200

    # Scribe B is gone
    response = client.get(f"/api/scribes/{scribe_b['id']}")
    assert response.status_code == 404


@pytest.mark.integration
def test_concurrent_entry_creation_by_multiple_users(client, faker):
    """Test that multiple users can create entries concurrently."""
    # Create multiple scribes
    scribes = [create_scribe(client, faker) for _ in range(5)]

    # Each scribe creates multiple entries
    expected_counts = {}
    for i, scribe in enumerate(scribes):
        num_entries = i + 2  # 2, 3, 4, 5, 6 entries
        expected_counts[scribe["id"]] = num_entries
        for _ in range(num_entries):
            response = client.post(
                "/api/entries",
                json={"content": faker.paragraph()},
                headers=scribe["auth_headers"],
            )
            assert response.status_code == 201

    # Verify each chronicle has correct count
    for scribe in scribes:
        response = client.get("/api/chronicle", headers=scribe["auth_headers"])
        assert len(response.get_json()["data"]) == expected_counts[scribe["id"]]


@pytest.mark.integration
def test_username_collision_attempts(client, faker):
    """Test that multiple users cannot have the same username."""
    # Create first scribe
    username = faker.user_name()
    scribe_a = client.post(
        "/api/auth/enlist",
        json={
            "username": username,
            "email": faker.email(),
            "password": faker.password(length=12),
        },
    )
    assert scribe_a.status_code == 201

    # Attempt to create another scribe with same username
    response = client.post(
        "/api/auth/enlist",
        json={
            "username": username,
            "email": faker.email(),
            "password": faker.password(length=12),
        },
    )
    assert response.status_code == 409


@pytest.mark.integration
def test_email_collision_attempts(client, faker):
    """Test that multiple users cannot have the same email."""
    # Create first scribe
    email = faker.email()
    scribe_a = client.post(
        "/api/auth/enlist",
        json={
            "username": faker.user_name(),
            "email": email,
            "password": faker.password(length=12),
        },
    )
    assert scribe_a.status_code == 201

    # Attempt to create another scribe with same email
    response = client.post(
        "/api/auth/enlist",
        json={
            "username": faker.user_name(),
            "email": email,
            "password": faker.password(length=12),
        },
    )
    assert response.status_code == 409


@pytest.mark.integration
def test_user_cannot_access_others_chronicle(client, faker):
    """Test that chronicle endpoint only returns authenticated user's entries."""
    # Create two scribes
    scribe_a = create_scribe(client, faker)
    scribe_b = create_scribe(client, faker)

    # Scribe A creates entries
    for _ in range(4):
        client.post(
            "/api/entries",
            json={"content": faker.paragraph()},
            headers=scribe_a["auth_headers"],
        )

    # Scribe B creates entries
    for _ in range(6):
        client.post(
            "/api/entries",
            json={"content": faker.paragraph()},
            headers=scribe_b["auth_headers"],
        )

    # Scribe A's chronicle only has 4 entries
    response = client.get("/api/chronicle", headers=scribe_a["auth_headers"])
    chronicle_a = response.get_json()["data"]
    assert len(chronicle_a) == 4
    for entry in chronicle_a:
        assert entry["attributes"]["scribeId"] == int(scribe_a["id"])

    # Scribe B's chronicle only has 6 entries
    response = client.get("/api/chronicle", headers=scribe_b["auth_headers"])
    chronicle_b = response.get_json()["data"]
    assert len(chronicle_b) == 6
    for entry in chronicle_b:
        assert entry["attributes"]["scribeId"] == int(scribe_b["id"])


@pytest.mark.integration
def test_entry_scribe_username_reflects_creator(client, faker):
    """Test that entries correctly identify their creator's username."""
    # Create multiple scribes
    scribes = [create_scribe(client, faker) for _ in range(3)]

    # Each scribe creates entries
    entry_ids = {}
    for scribe in scribes:
        response = client.post(
            "/api/entries",
            json={"content": faker.paragraph(), "visibility": "public"},
            headers=scribe["auth_headers"],
        )
        entry_ids[scribe["username"]] = response.get_json()["data"]["id"]

    # Verify each entry has correct scribeUsername
    for username, entry_id in entry_ids.items():
        response = client.get(f"/api/entries/{entry_id}")
        assert response.status_code == 200
        assert response.get_json()["data"]["attributes"]["scribeUsername"] == username


@pytest.mark.integration
def test_multiple_users_updating_own_entries_simultaneously(client, faker):
    """Test that multiple users can update their own entries without interference."""
    # Create multiple scribes with entries
    scribes = []
    for _ in range(4):
        scribe = create_scribe(client, faker)
        response = client.post(
            "/api/entries",
            json={"content": faker.paragraph()},
            headers=scribe["auth_headers"],
        )
        scribe["entry_id"] = response.get_json()["data"]["id"]
        scribes.append(scribe)

    # Each scribe updates their own entry
    new_contents = {}
    for scribe in scribes:
        new_content = faker.paragraph()
        new_contents[scribe["entry_id"]] = new_content
        response = client.patch(
            f"/api/entries/{scribe['entry_id']}",
            json={"content": new_content},
            headers=scribe["auth_headers"],
        )
        assert response.status_code == 200

    # Verify each entry has the correct updated content
    for entry_id, expected_content in new_contents.items():
        response = client.get(f"/api/entries/{entry_id}")
        assert response.status_code == 200
        assert response.get_json()["data"]["attributes"]["content"] == expected_content


@pytest.mark.integration
def test_profile_updates_do_not_affect_other_users(client, faker):
    """Test that profile updates are isolated to the updating user."""
    # Create multiple scribes
    scribes = [create_scribe(client, faker) for _ in range(3)]

    # Store original profile data
    original_profiles = {}
    for scribe in scribes:
        response = client.get(f"/api/scribes/{scribe['id']}")
        original_profiles[scribe["id"]] = response.get_json()["data"]["attributes"]

    # First scribe updates their profile
    new_bio = faker.text(max_nb_chars=150)
    new_email = faker.email()
    response = client.patch(
        f"/api/scribes/{scribes[0]['id']}",
        json={"bio": new_bio, "email": new_email},
        headers=scribes[0]["auth_headers"],
    )
    assert response.status_code == 200

    # Verify other scribes' profiles unchanged
    for i in range(1, len(scribes)):
        response = client.get(f"/api/scribes/{scribes[i]['id']}")
        current_profile = response.get_json()["data"]["attributes"]
        original = original_profiles[scribes[i]["id"]]
        assert current_profile["email"] == original["email"]
        assert current_profile["bio"] == original["bio"]
        assert current_profile["username"] == original["username"]


@pytest.mark.integration
def test_viewing_nonexistent_scribe_returns_404_for_all(client, faker):
    """Test that all users get 404 when viewing nonexistent scribe."""
    # Create a scribe
    scribe = create_scribe(client, faker)

    nonexistent_id = "99999"

    # Authenticated user gets 404
    response = client.get(
        f"/api/scribes/{nonexistent_id}", headers=scribe["auth_headers"]
    )
    assert response.status_code == 404

    # Unauthenticated user also gets 404
    response = client.get(f"/api/scribes/{nonexistent_id}")
    assert response.status_code == 404


@pytest.mark.integration
def test_private_entries_hidden_from_public_entry_listing(client, faker):
    """Test that private entries cannot be discovered by other users."""
    # Create two scribes
    scribe_a = create_scribe(client, faker)
    scribe_b = create_scribe(client, faker)

    # Scribe A creates several entries with sequential IDs
    entry_ids = []
    for i in range(10):
        visibility = "private" if i % 3 == 0 else "public"
        response = client.post(
            "/api/entries",
            json={"content": faker.paragraph(), "visibility": visibility},
            headers=scribe_a["auth_headers"],
        )
        entry_ids.append({
            "id": response.get_json()["data"]["id"],
            "visibility": visibility
        })

    # Scribe B tries to access all entries
    for entry in entry_ids:
        response = client.get(
            f"/api/entries/{entry['id']}", headers=scribe_b["auth_headers"]
        )
        if entry["visibility"] == "public":
            assert response.status_code == 200
        else:
            assert response.status_code == 404


@pytest.mark.integration
def test_cross_user_authentication_attempts(client, faker):
    """Test that users cannot authenticate with another user's credentials."""
    # Create two scribes
    scribe_a = create_scribe(client, faker)
    scribe_b = create_scribe(client, faker)

    # Try to authenticate as Scribe A with Scribe B's password
    wrong_auth = {
        "Authorization": f'Basic {b64encode(f"{scribe_a["username"]}:{scribe_b["password"]}".encode()).decode()}'
    }
    response = client.post("/api/auth/unlock", headers=wrong_auth)
    assert response.status_code == 401

    # Try to authenticate as Scribe B with Scribe A's password
    wrong_auth = {
        "Authorization": f'Basic {b64encode(f"{scribe_b["username"]}:{scribe_a["password"]}".encode()).decode()}'
    }
    response = client.post("/api/auth/unlock", headers=wrong_auth)
    assert response.status_code == 401


@pytest.mark.integration
def test_realistic_multi_user_interaction_scenario(client, faker):
    """Test a realistic scenario with multiple users interacting over time."""
    # Create three scribes: Alice, Bob, and Charlie
    alice = create_scribe(client, faker)
    bob = create_scribe(client, faker)
    charlie = create_scribe(client, faker)

    # Alice creates some public entries
    alice_public_entries = []
    for _ in range(3):
        response = client.post(
            "/api/entries",
            json={"content": faker.paragraph(), "visibility": "public"},
            headers=alice["auth_headers"],
        )
        alice_public_entries.append(response.get_json()["data"]["id"])

    # Alice creates a private entry
    response = client.post(
        "/api/entries",
        json={"content": faker.paragraph(), "visibility": "private"},
        headers=alice["auth_headers"],
    )
    alice_private_entry = response.get_json()["data"]["id"]

    # Bob views Alice's public entries (should succeed)
    for entry_id in alice_public_entries:
        response = client.get(f"/api/entries/{entry_id}", headers=bob["auth_headers"])
        assert response.status_code == 200

    # Bob tries to view Alice's private entry (should fail)
    response = client.get(
        f"/api/entries/{alice_private_entry}", headers=bob["auth_headers"]
    )
    assert response.status_code == 404

    # Bob creates his own entries
    for _ in range(5):
        client.post(
            "/api/entries",
            json={"content": faker.paragraph()},
            headers=bob["auth_headers"],
        )

    # Charlie creates entries
    for _ in range(2):
        client.post(
            "/api/entries",
            json={"content": faker.paragraph()},
            headers=charlie["auth_headers"],
        )

    # Verify each user's chronicle is separate
    alice_chronicle = client.get("/api/chronicle", headers=alice["auth_headers"])
    assert len(alice_chronicle.get_json()["data"]) == 4  # 3 public + 1 private

    bob_chronicle = client.get("/api/chronicle", headers=bob["auth_headers"])
    assert len(bob_chronicle.get_json()["data"]) == 5

    charlie_chronicle = client.get("/api/chronicle", headers=charlie["auth_headers"])
    assert len(charlie_chronicle.get_json()["data"]) == 2

    # Alice updates her profile
    client.patch(
        f"/api/scribes/{alice['id']}",
        json={"bio": faker.text(max_nb_chars=100)},
        headers=alice["auth_headers"],
    )

    # Bob and Charlie can view Alice's updated profile
    alice_profile = client.get(f"/api/scribes/{alice['id']}")
    assert alice_profile.status_code == 200

    bob_profile = client.get(f"/api/scribes/{bob['id']}")
    assert bob_profile.status_code == 200

    charlie_profile = client.get(f"/api/scribes/{charlie['id']}")
    assert charlie_profile.status_code == 200
