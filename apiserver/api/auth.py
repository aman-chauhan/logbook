"""Authentication endpoints for Logbook API.

This module provides endpoints for scribe account creation and authentication:
- POST /api/auth/enlist - Create a new scribe account
- POST /api/auth/unlock - Verify credentials (login)
- POST /api/auth/lock - Logout (informational endpoint, stateless)
"""

from flask import request, jsonify
from sqlalchemy.exc import IntegrityError
from . import api_bp
from ..auth import require_auth
from ..models import Scribe
from ..extensions import db


@api_bp.route("/auth/enlist", methods=["POST"])
def enlist():
    """Create a new scribe account.

    Request Body (JSON):
        {
            "username": "string (required)",
            "email": "string (required)",
            "password": "string (required)"
        }

    Returns:
        201 Created: Scribe account created successfully
        400 Bad Request: Missing required fields
        409 Conflict: Username or email already exists

    Example:
        curl -X POST http://localhost:5000/api/auth/enlist \\
             -H "Content-Type: application/json" \\
             -d '{"username": "alice", "email": "alice@example.com", "password": "secret123"}'
    """
    data = request.get_json()

    # Validate required fields
    if not data:
        return (
            jsonify(
                {
                    "errors": [
                        {
                            "status": "400",
                            "title": "Invalid Request",
                            "detail": "Request body must be valid JSON",
                        }
                    ]
                }
            ),
            400,
        )

    missing_fields = []
    if "username" not in data:
        missing_fields.append("username")
    if "email" not in data:
        missing_fields.append("email")
    if "password" not in data:
        missing_fields.append("password")

    if missing_fields:
        return (
            jsonify(
                {
                    "errors": [
                        {
                            "status": "400",
                            "title": "Missing Required Fields",
                            "detail": f"The following fields are required: {', '.join(missing_fields)}",
                        }
                    ]
                }
            ),
            400,
        )

    # Create new scribe
    scribe = Scribe(username=data["username"], email=data["email"])
    scribe.set_password(data["password"])

    # Add optional bio field if provided
    if "bio" in data:
        scribe.bio = data["bio"]

    try:
        db.session.add(scribe)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        # Check which field caused the conflict
        existing_username = Scribe.query.filter_by(username=data["username"]).first()
        existing_email = Scribe.query.filter_by(email=data["email"]).first()

        if existing_username:
            return (
                jsonify(
                    {
                        "errors": [
                            {
                                "status": "409",
                                "title": "Username Already Exists",
                                "detail": f"The username '{data['username']}' is already taken",
                            }
                        ]
                    }
                ),
                409,
            )
        elif existing_email:
            return (
                jsonify(
                    {
                        "errors": [
                            {
                                "status": "409",
                                "title": "Email Already Exists",
                                "detail": f"The email '{data['email']}' is already registered",
                            }
                        ]
                    }
                ),
                409,
            )
        else:
            # Generic integrity error (shouldn't happen, but just in case)
            return (
                jsonify(
                    {
                        "errors": [
                            {
                                "status": "409",
                                "title": "Conflict",
                                "detail": "A scribe with this username or email already exists",
                            }
                        ]
                    }
                ),
                409,
            )

    # Return created scribe (without password_hash)
    return jsonify({"data": scribe.to_jsonapi()}), 201


@api_bp.route("/auth/unlock", methods=["POST"])
@require_auth
def unlock(current_scribe):
    """Verify credentials and return scribe information.

    This endpoint validates HTTP Basic Auth credentials and returns the
    authenticated scribe's profile. It serves as a "login" endpoint, though
    the API uses stateless authentication.

    Authentication:
        HTTP Basic Auth required

    Returns:
        200 OK: Valid credentials
        401 Unauthorized: Invalid or missing credentials

    Example:
        curl -X POST http://localhost:5000/api/auth/unlock \\
             -u alice:secret123 \\
             -H "Accept: application/vnd.api+json"
    """
    # If we got here, authentication was successful (handled by @require_auth)
    return jsonify({"data": current_scribe.to_jsonapi()}), 200


@api_bp.route("/auth/lock", methods=["POST"])
@require_auth
def lock(current_scribe):
    """Lock logbook (logout).

    This is an informational endpoint since the API uses stateless HTTP Basic Auth.
    There's no server-side session to invalidate. Clients should stop sending
    credentials after calling this endpoint.

    Authentication:
        HTTP Basic Auth required

    Returns:
        204 No Content: Successfully acknowledged logout

    Example:
        curl -X POST http://localhost:5000/api/auth/lock \\
             -u alice:secret123 \\
             -i  # -i flag shows 204 status code
    """
    # Return 204 No Content (empty response body)
    # This is informational only - there's no session to invalidate
    return "", 204
