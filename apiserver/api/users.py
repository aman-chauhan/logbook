"""Scribe profile endpoints for Logbook API.

This module provides endpoints for viewing and managing scribe profiles:
- GET /api/scribes/<id> - View scribe profile (public)
- PATCH /api/scribes/<id> - Update own profile (authenticated)
- DELETE /api/scribes/<id> - Delete own account (authenticated)
"""

from flask import request, jsonify
from sqlalchemy.exc import IntegrityError
from . import api_bp
from ..auth import require_auth
from ..models import Scribe
from ..extensions import db


@api_bp.route("/scribes/<int:scribe_id>", methods=["GET"])
def get_scribe(scribe_id):
    """Get scribe profile by ID.

    This is a public endpoint - no authentication required.
    Returns basic profile information without sensitive data.

    Args:
        scribe_id: The ID of the scribe to retrieve

    Returns:
        200 OK: Scribe profile found
        404 Not Found: Scribe does not exist

    Example:
        curl -X GET http://localhost:5000/api/scribes/1 \\
             -H "Accept: application/vnd.api+json"
    """
    scribe = Scribe.query.get(scribe_id)

    if not scribe:
        return (
            jsonify(
                {
                    "errors": [
                        {
                            "status": "404",
                            "title": "Scribe Not Found",
                            "detail": f"No scribe exists with ID {scribe_id}",
                        }
                    ]
                }
            ),
            404,
        )

    return jsonify({"data": scribe.to_jsonapi()}), 200


@api_bp.route("/scribes/<int:scribe_id>", methods=["PATCH"])
@require_auth
def update_scribe(current_scribe, scribe_id):
    """Update scribe profile.

    Scribes can only update their own profile. Supports updating:
    - email (must be unique)
    - bio
    - password (via 'password' field)

    Authentication:
        HTTP Basic Auth required

    Args:
        current_scribe: Authenticated scribe (from @require_auth)
        scribe_id: The ID of the scribe to update

    Returns:
        200 OK: Profile updated successfully
        400 Bad Request: Invalid request data
        403 Forbidden: Attempting to update another scribe's profile
        404 Not Found: Scribe does not exist
        409 Conflict: Email already in use

    Example:
        curl -X PATCH http://localhost:5000/api/scribes/1 \\
             -u alice:secret123 \\
             -H "Content-Type: application/json" \\
             -d '{"email": "newemail@example.com", "bio": "Updated bio"}'
    """
    # Check if scribe exists
    scribe = Scribe.query.get(scribe_id)

    if not scribe:
        return (
            jsonify(
                {
                    "errors": [
                        {
                            "status": "404",
                            "title": "Scribe Not Found",
                            "detail": f"No scribe exists with ID {scribe_id}",
                        }
                    ]
                }
            ),
            404,
        )

    # Check ownership - scribes can only update their own profile
    if current_scribe.id != scribe_id:
        return (
            jsonify(
                {
                    "errors": [
                        {
                            "status": "403",
                            "title": "Forbidden",
                            "detail": "You can only update your own profile",
                        }
                    ]
                }
            ),
            403,
        )

    # Get request data
    data = request.get_json()

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

    # Update allowed fields
    if "email" in data:
        scribe.email = data["email"]

    if "bio" in data:
        scribe.bio = data["bio"]

    if "password" in data:
        scribe.set_password(data["password"])

    # Try to commit changes
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        # Email must be unique
        existing_email = Scribe.query.filter_by(email=data.get("email")).first()

        if existing_email and existing_email.id != scribe_id:
            return (
                jsonify(
                    {
                        "errors": [
                            {
                                "status": "409",
                                "title": "Email Already Exists",
                                "detail": f"The email '{data['email']}' is already registered to another scribe",
                            }
                        ]
                    }
                ),
                409,
            )
        else:
            # Generic integrity error
            return (
                jsonify(
                    {
                        "errors": [
                            {
                                "status": "409",
                                "title": "Conflict",
                                "detail": "Unable to update profile due to a data conflict",
                            }
                        ]
                    }
                ),
                409,
            )

    return jsonify({"data": scribe.to_jsonapi()}), 200


@api_bp.route("/scribes/<int:scribe_id>", methods=["DELETE"])
@require_auth
def delete_scribe(current_scribe, scribe_id):
    """Delete scribe account.

    Scribes can only delete their own account. This will cascade delete
    all entries associated with the scribe (configured in the Entry model).

    Authentication:
        HTTP Basic Auth required

    Args:
        current_scribe: Authenticated scribe (from @require_auth)
        scribe_id: The ID of the scribe to delete

    Returns:
        204 No Content: Account deleted successfully
        403 Forbidden: Attempting to delete another scribe's account
        404 Not Found: Scribe does not exist

    Example:
        curl -X DELETE http://localhost:5000/api/scribes/1 \\
             -u alice:secret123 \\
             -i  # -i flag shows 204 status code
    """
    # Check if scribe exists
    scribe = Scribe.query.get(scribe_id)

    if not scribe:
        return (
            jsonify(
                {
                    "errors": [
                        {
                            "status": "404",
                            "title": "Scribe Not Found",
                            "detail": f"No scribe exists with ID {scribe_id}",
                        }
                    ]
                }
            ),
            404,
        )

    # Check ownership - scribes can only delete their own account
    if current_scribe.id != scribe_id:
        return (
            jsonify(
                {
                    "errors": [
                        {
                            "status": "403",
                            "title": "Forbidden",
                            "detail": "You can only delete your own account",
                        }
                    ]
                }
            ),
            403,
        )

    # Delete scribe (cascade deletes entries automatically)
    db.session.delete(scribe)
    db.session.commit()

    # Return 204 No Content (empty response body)
    return "", 204
