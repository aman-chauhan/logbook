"""Integration tests for authentication flows.

Tests complete authentication state transitions and security scenarios
using realistic Faker-generated data.
"""

import pytest
from base64 import b64encode


@pytest.mark.integration
def test_complete_auth_cycle(client, faker):
    """Test complete authentication cycle: enlist -> unlock -> operations -> lock."""
    # Step 1: Enlist
    username = faker.user_name()
    email = faker.email()
    password = faker.password(length=12)

    response = client.post(
        "/api/auth/enlist",
        json={"username": username, "email": email, "password": password},
    )
    assert response.status_code == 201
    scribe_id = response.get_json()["data"]["id"]

    auth_headers = {
        "Authorization": f'Basic {b64encode(f"{username}:{password}".encode()).decode()}'
    }

    # Step 2: Unlock (verify credentials)
    response = client.post("/api/auth/unlock", headers=auth_headers)
    assert response.status_code == 200
    assert response.get_json()["data"]["id"] == scribe_id

    # Step 3: Perform operations
    response = client.post(
        "/api/entries",
        json={"content": faker.paragraph()},
        headers=auth_headers,
    )
    assert response.status_code == 201

    response = client.get("/api/chronicle", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.get_json()["data"]) == 1

    # Step 4: Lock
    response = client.post("/api/auth/lock", headers=auth_headers)
    assert response.status_code == 204

    # Step 5: Can still unlock (stateless API)
    response = client.post("/api/auth/unlock", headers=auth_headers)
    assert response.status_code == 200


@pytest.mark.integration
def test_authentication_required_for_protected_endpoints(client, faker):
    """Test that protected endpoints require authentication."""
    # Attempt to access protected endpoints without auth

    # Chronicle
    response = client.get("/api/chronicle")
    assert response.status_code == 401

    # Create entry
    response = client.post("/api/entries", json={"content": faker.paragraph()})
    assert response.status_code == 401

    # Update profile (nonexistent ID)
    response = client.patch("/api/scribes/1", json={"bio": faker.text(max_nb_chars=100)})
    assert response.status_code == 401

    # Delete profile (nonexistent ID)
    response = client.delete("/api/scribes/1")
    assert response.status_code == 401

    # Update entry (nonexistent ID)
    response = client.patch("/api/entries/1", json={"content": faker.paragraph()})
    assert response.status_code == 401

    # Delete entry (nonexistent ID)
    response = client.delete("/api/entries/1")
    assert response.status_code == 401


@pytest.mark.integration
def test_invalid_credentials_rejected(client, faker):
    """Test that invalid credentials are properly rejected."""
    # Create a valid scribe
    username = faker.user_name()
    email = faker.email()
    password = faker.password(length=12)

    client.post(
        "/api/auth/enlist",
        json={"username": username, "email": email, "password": password},
    )

    # Try with wrong password
    wrong_auth = {
        "Authorization": f'Basic {b64encode(f"{username}:wrongpassword".encode()).decode()}'
    }
    response = client.post("/api/auth/unlock", headers=wrong_auth)
    assert response.status_code == 401

    # Try with wrong username
    wrong_auth = {
        "Authorization": f'Basic {b64encode(f"wronguser:{password}".encode()).decode()}'
    }
    response = client.post("/api/auth/unlock", headers=wrong_auth)
    assert response.status_code == 401

    # Try with both wrong
    wrong_auth = {
        "Authorization": f'Basic {b64encode(f"wronguser:wrongpassword".encode()).decode()}'
    }
    response = client.post("/api/auth/unlock", headers=wrong_auth)
    assert response.status_code == 401


@pytest.mark.integration
def test_authentication_persists_across_requests(client, faker):
    """Test that credentials work across multiple requests."""
    # Enlist
    username = faker.user_name()
    email = faker.email()
    password = faker.password(length=12)

    client.post(
        "/api/auth/enlist",
        json={"username": username, "email": email, "password": password},
    )

    auth_headers = {
        "Authorization": f'Basic {b64encode(f"{username}:{password}".encode()).decode()}'
    }

    # Multiple operations with same credentials
    for i in range(5):
        # Create entry
        response = client.post(
            "/api/entries",
            json={"content": faker.paragraph()},
            headers=auth_headers,
        )
        assert response.status_code == 201

        # View chronicle
        response = client.get("/api/chronicle", headers=auth_headers)
        assert response.status_code == 200
        assert len(response.get_json()["data"]) == i + 1

        # Unlock
        response = client.post("/api/auth/unlock", headers=auth_headers)
        assert response.status_code == 200


@pytest.mark.integration
def test_password_change_invalidates_old_credentials(client, faker):
    """Test that old password no longer works after password change."""
    # Enlist
    username = faker.user_name()
    email = faker.email()
    old_password = faker.password(length=12)

    response = client.post(
        "/api/auth/enlist",
        json={"username": username, "email": email, "password": old_password},
    )
    scribe_id = response.get_json()["data"]["id"]

    old_auth = {
        "Authorization": f'Basic {b64encode(f"{username}:{old_password}".encode()).decode()}'
    }

    # Verify old credentials work
    response = client.post("/api/auth/unlock", headers=old_auth)
    assert response.status_code == 200

    # Change password
    new_password = faker.password(length=12)
    response = client.patch(
        f"/api/scribes/{scribe_id}",
        json={"password": new_password},
        headers=old_auth,
    )
    assert response.status_code == 200

    # Old credentials should fail
    response = client.post("/api/auth/unlock", headers=old_auth)
    assert response.status_code == 401

    # New credentials should work
    new_auth = {
        "Authorization": f'Basic {b64encode(f"{username}:{new_password}".encode()).decode()}'
    }
    response = client.post("/api/auth/unlock", headers=new_auth)
    assert response.status_code == 200


@pytest.mark.integration
def test_deleted_account_authentication_fails(client, faker):
    """Test that authentication fails for deleted accounts."""
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

    # Verify authentication works
    response = client.post("/api/auth/unlock", headers=auth_headers)
    assert response.status_code == 200

    # Delete account
    response = client.delete(f"/api/scribes/{scribe_id}", headers=auth_headers)
    assert response.status_code == 204

    # Authentication should now fail
    response = client.post("/api/auth/unlock", headers=auth_headers)
    assert response.status_code == 401

    # Cannot create entries
    response = client.post(
        "/api/entries",
        json={"content": faker.paragraph()},
        headers=auth_headers,
    )
    assert response.status_code == 401


@pytest.mark.integration
def test_authentication_with_special_characters_in_password(client, faker):
    """Test authentication with special characters in password."""
    username = faker.user_name()
    email = faker.email()
    # Password with special characters
    password = "P@ssw0rd!#$%^&*()_+-=[]{}|;:',.<>?/~`"

    # Enlist with special character password
    response = client.post(
        "/api/auth/enlist",
        json={"username": username, "email": email, "password": password},
    )
    assert response.status_code == 201

    auth_headers = {
        "Authorization": f'Basic {b64encode(f"{username}:{password}".encode()).decode()}'
    }

    # Verify authentication works
    response = client.post("/api/auth/unlock", headers=auth_headers)
    assert response.status_code == 200

    # Verify can perform operations
    response = client.post(
        "/api/entries",
        json={"content": faker.paragraph()},
        headers=auth_headers,
    )
    assert response.status_code == 201


@pytest.mark.integration
def test_multiple_failed_auth_attempts_then_success(client, faker):
    """Test that correct credentials work after failed attempts."""
    # Enlist
    username = faker.user_name()
    email = faker.email()
    password = faker.password(length=12)

    client.post(
        "/api/auth/enlist",
        json={"username": username, "email": email, "password": password},
    )

    # Multiple failed attempts
    for _ in range(5):
        wrong_auth = {
            "Authorization": f'Basic {b64encode(f"{username}:wrongpass".encode()).decode()}'
        }
        response = client.post("/api/auth/unlock", headers=wrong_auth)
        assert response.status_code == 401

    # Correct credentials should still work
    correct_auth = {
        "Authorization": f'Basic {b64encode(f"{username}:{password}".encode()).decode()}'
    }
    response = client.post("/api/auth/unlock", headers=correct_auth)
    assert response.status_code == 200


@pytest.mark.integration
def test_auth_flow_with_profile_updates(client, faker):
    """Test authentication flow remains functional through profile updates."""
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

    # Unlock
    response = client.post("/api/auth/unlock", headers=auth_headers)
    assert response.status_code == 200

    # Update email
    new_email = faker.email()
    response = client.patch(
        f"/api/scribes/{scribe_id}",
        json={"email": new_email},
        headers=auth_headers,
    )
    assert response.status_code == 200

    # Auth still works with username (email doesn't affect username auth)
    response = client.post("/api/auth/unlock", headers=auth_headers)
    assert response.status_code == 200

    # Update bio
    response = client.patch(
        f"/api/scribes/{scribe_id}",
        json={"bio": faker.text(max_nb_chars=200)},
        headers=auth_headers,
    )
    assert response.status_code == 200

    # Auth still works
    response = client.post("/api/auth/unlock", headers=auth_headers)
    assert response.status_code == 200


@pytest.mark.integration
def test_auth_with_operations_across_all_endpoints(client, faker):
    """Test authentication flow across all API endpoints."""
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

    # Unlock
    response = client.post("/api/auth/unlock", headers=auth_headers)
    assert response.status_code == 200

    # View own profile (no auth required but include it)
    response = client.get(f"/api/scribes/{scribe_id}", headers=auth_headers)
    assert response.status_code == 200

    # Update profile
    response = client.patch(
        f"/api/scribes/{scribe_id}",
        json={"bio": faker.text(max_nb_chars=100)},
        headers=auth_headers,
    )
    assert response.status_code == 200

    # Create entry
    response = client.post(
        "/api/entries",
        json={"content": faker.paragraph()},
        headers=auth_headers,
    )
    assert response.status_code == 201
    entry_id = response.get_json()["data"]["id"]

    # View entry
    response = client.get(f"/api/entries/{entry_id}", headers=auth_headers)
    assert response.status_code == 200

    # Update entry
    response = client.patch(
        f"/api/entries/{entry_id}",
        json={"content": faker.paragraph()},
        headers=auth_headers,
    )
    assert response.status_code == 200

    # View chronicle
    response = client.get("/api/chronicle", headers=auth_headers)
    assert response.status_code == 200

    # Delete entry
    response = client.delete(f"/api/entries/{entry_id}", headers=auth_headers)
    assert response.status_code == 204

    # Lock
    response = client.post("/api/auth/lock", headers=auth_headers)
    assert response.status_code == 204

    # Delete account
    response = client.delete(f"/api/scribes/{scribe_id}", headers=auth_headers)
    assert response.status_code == 204


@pytest.mark.integration
def test_auth_isolation_between_users(client, faker):
    """Test that authentication is properly isolated between users."""
    # Create two scribes
    user1 = {
        "username": faker.user_name(),
        "email": faker.email(),
        "password": faker.password(length=12),
    }
    user2 = {
        "username": faker.user_name(),
        "email": faker.email(),
        "password": faker.password(length=12),
    }

    # Enlist both
    response = client.post("/api/auth/enlist", json=user1)
    user1_id = response.get_json()["data"]["id"]

    response = client.post("/api/auth/enlist", json=user2)
    user2_id = response.get_json()["data"]["id"]

    # Create auth headers
    user1_username = user1["username"]
    user1_password = user1["password"]
    user2_username = user2["username"]
    user2_password = user2["password"]
    user1_auth = {
        "Authorization": f"Basic {b64encode(f'{user1_username}:{user1_password}'.encode()).decode()}"
    }
    user2_auth = {
        "Authorization": f"Basic {b64encode(f'{user2_username}:{user2_password}'.encode()).decode()}"
    }

    # User 1 can authenticate
    response = client.post("/api/auth/unlock", headers=user1_auth)
    assert response.status_code == 200
    assert response.get_json()["data"]["id"] == user1_id

    # User 2 can authenticate
    response = client.post("/api/auth/unlock", headers=user2_auth)
    assert response.status_code == 200
    assert response.get_json()["data"]["id"] == user2_id

    # User 1 creates entry
    response = client.post(
        "/api/entries",
        json={"content": faker.paragraph()},
        headers=user1_auth,
    )
    entry1_id = response.get_json()["data"]["id"]

    # User 2 creates entry
    response = client.post(
        "/api/entries",
        json={"content": faker.paragraph()},
        headers=user2_auth,
    )
    entry2_id = response.get_json()["data"]["id"]

    # User 1 cannot modify User 2's entry
    response = client.patch(
        f"/api/entries/{entry2_id}",
        json={"content": faker.paragraph()},
        headers=user1_auth,
    )
    assert response.status_code == 403

    # User 2 cannot modify User 1's entry
    response = client.patch(
        f"/api/entries/{entry1_id}",
        json={"content": faker.paragraph()},
        headers=user2_auth,
    )
    assert response.status_code == 403


@pytest.mark.integration
def test_missing_authorization_header(client, faker):
    """Test that missing authorization header returns proper error."""
    # Try to access protected endpoints without any authorization header
    response = client.post("/api/auth/unlock")
    assert response.status_code == 401
    assert "errors" in response.get_json()

    response = client.get("/api/chronicle")
    assert response.status_code == 401
    assert "errors" in response.get_json()

    response = client.post("/api/entries", json={"content": faker.paragraph()})
    assert response.status_code == 401
    assert "errors" in response.get_json()


@pytest.mark.integration
def test_malformed_authorization_header(client, faker):
    """Test that malformed authorization headers are handled properly."""
    # Invalid Base64
    response = client.post(
        "/api/auth/unlock",
        headers={"Authorization": "Basic not-valid-base64!!!"},
    )
    assert response.status_code == 401

    # Missing "Basic" prefix
    response = client.post(
        "/api/auth/unlock",
        headers={"Authorization": b64encode(b"user:pass").decode()},
    )
    assert response.status_code == 401

    # Empty authorization
    response = client.post("/api/auth/unlock", headers={"Authorization": ""})
    assert response.status_code == 401


@pytest.mark.integration
def test_auth_with_unicode_username_and_password(client, faker):
    """Test authentication with Unicode characters in credentials."""
    # Username and password with Unicode
    username = faker.user_name() + "_测试"
    email = faker.email()
    password = faker.password(length=12) + "_密码"

    # Enlist
    response = client.post(
        "/api/auth/enlist",
        json={"username": username, "email": email, "password": password},
    )
    assert response.status_code == 201

    auth_headers = {
        "Authorization": f'Basic {b64encode(f"{username}:{password}".encode("utf-8")).decode()}'
    }

    # Unlock should work
    response = client.post("/api/auth/unlock", headers=auth_headers)
    assert response.status_code == 200

    # Operations should work
    response = client.post(
        "/api/entries",
        json={"content": faker.paragraph()},
        headers=auth_headers,
    )
    assert response.status_code == 201


@pytest.mark.integration
def test_lock_endpoint_idempotency(client, faker):
    """Test that lock endpoint can be called multiple times safely."""
    # Enlist
    username = faker.user_name()
    email = faker.email()
    password = faker.password(length=12)

    client.post(
        "/api/auth/enlist",
        json={"username": username, "email": email, "password": password},
    )

    auth_headers = {
        "Authorization": f'Basic {b64encode(f"{username}:{password}".encode()).decode()}'
    }

    # Lock multiple times
    for _ in range(5):
        response = client.post("/api/auth/lock", headers=auth_headers)
        assert response.status_code == 204

    # Still can unlock (stateless)
    response = client.post("/api/auth/unlock", headers=auth_headers)
    assert response.status_code == 200
