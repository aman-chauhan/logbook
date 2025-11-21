"""Entry endpoints for Logbook API.

This module provides endpoints for managing entries (posts):
- POST /api/entries - Create a new entry
- GET /api/entries/<id> - View a single entry
- PATCH /api/entries/<id> - Update an entry
- DELETE /api/entries/<id> - Delete an entry
- GET /api/chronicle - View authenticated scribe's entries
"""

from flask import request, jsonify
from . import api_bp
from ..auth import require_auth, optional_auth
from ..models import Entry
from ..extensions import db


@api_bp.route("/entries", methods=["POST"])
@require_auth
def create_entry(current_scribe):
    """Create a new entry.

    Creates an entry for the authenticated scribe. The entry can be
    public (visible to all) or private (visible only to the owner).

    Authentication:
        HTTP Basic Auth required

    Request Body (JSON):
        {
            "content": "string (required)",
            "visibility": "string (optional, default: 'public')"
        }

    Args:
        current_scribe: Authenticated scribe (from @require_auth)

    Returns:
        201 Created: Entry created successfully
        400 Bad Request: Missing required fields or invalid data

    Example:
        curl -X POST http://localhost:5000/api/entries \\
             -u alice:secret123 \\
             -H "Content-Type: application/json" \\
             -d '{"content": "My first entry!", "visibility": "public"}'
    """
    data = request.get_json()

    # Validate request body
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

    # Validate required fields
    if "content" not in data:
        return (
            jsonify(
                {
                    "errors": [
                        {
                            "status": "400",
                            "title": "Missing Required Field",
                            "detail": "The content field is required",
                        }
                    ]
                }
            ),
            400,
        )

    # Validate visibility if provided
    visibility = data.get("visibility", "public")
    if visibility not in ["public", "private"]:
        return (
            jsonify(
                {
                    "errors": [
                        {
                            "status": "400",
                            "title": "Invalid Visibility",
                            "detail": "Visibility must be either 'public' or 'private'",
                        }
                    ]
                }
            ),
            400,
        )

    # Create entry
    entry = Entry(
        content=data["content"],
        scribe_id=current_scribe.id,
        visibility=visibility,
    )

    db.session.add(entry)
    db.session.commit()

    return jsonify({"data": entry.to_jsonapi()}), 201


@api_bp.route("/entries/<string:entry_id>", methods=["GET"])
@optional_auth
def get_entry(current_scribe, entry_id):
    """Get a single entry by ID.

    Public entries can be viewed by anyone (authenticated or not).
    Private entries can only be viewed by the owner. Non-owners will
    receive a 404 error to hide the existence of private entries.

    Authentication:
        Optional (required for private entries owned by the requester)

    Args:
        current_scribe: Authenticated scribe or None (from @optional_auth)
        entry_id: The UUID of the entry to retrieve

    Returns:
        200 OK: Entry found and accessible
        404 Not Found: Entry does not exist or is private and not owned by requester

    Example (public entry):
        curl -X GET http://localhost:5000/api/entries/550e8400-e29b-41d4-a716-446655440000 \\
             -H "Accept: application/vnd.api+json"

    Example (private entry):
        curl -X GET http://localhost:5000/api/entries/550e8400-e29b-41d4-a716-446655440001 \\
             -u alice:secret123 \\
             -H "Accept: application/vnd.api+json"
    """
    entry = db.session.get(Entry, entry_id)

    # Return 404 if entry doesn't exist
    if not entry:
        return (
            jsonify(
                {
                    "errors": [
                        {
                            "status": "404",
                            "title": "Entry Not Found",
                            "detail": f"No entry exists with ID {entry_id}",
                        }
                    ]
                }
            ),
            404,
        )

    # Check access permissions for private entries
    # Return 404 (not 403) to hide existence from non-owners
    if entry.visibility == "private":
        if not current_scribe or current_scribe.id != entry.scribe_id:
            return (
                jsonify(
                    {
                        "errors": [
                            {
                                "status": "404",
                                "title": "Entry Not Found",
                                "detail": f"No entry exists with ID {entry_id}",
                            }
                        ]
                    }
                ),
                404,
            )

    return jsonify({"data": entry.to_jsonapi()}), 200


@api_bp.route("/entries/<string:entry_id>", methods=["PATCH"])
@require_auth
def update_entry(current_scribe, entry_id):
    """Update an entry.

    Scribes can only update their own entries. Supports updating:
    - content
    - visibility

    Authentication:
        HTTP Basic Auth required

    Args:
        current_scribe: Authenticated scribe (from @require_auth)
        entry_id: The UUID of the entry to update

    Returns:
        200 OK: Entry updated successfully
        400 Bad Request: Invalid request data
        403 Forbidden: Attempting to update another scribe's entry
        404 Not Found: Entry does not exist

    Example:
        curl -X PATCH http://localhost:5000/api/entries/550e8400-e29b-41d4-a716-446655440000 \\
             -u alice:secret123 \\
             -H "Content-Type: application/json" \\
             -d '{"content": "Updated content", "visibility": "private"}'
    """
    entry = db.session.get(Entry, entry_id)

    # Return 404 if entry doesn't exist
    if not entry:
        return (
            jsonify(
                {
                    "errors": [
                        {
                            "status": "404",
                            "title": "Entry Not Found",
                            "detail": f"No entry exists with ID {entry_id}",
                        }
                    ]
                }
            ),
            404,
        )

    # Check ownership - scribes can only update their own entries
    if current_scribe.id != entry.scribe_id:
        return (
            jsonify(
                {
                    "errors": [
                        {
                            "status": "403",
                            "title": "Forbidden",
                            "detail": "You can only update your own entries",
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
    if "content" in data:
        entry.content = data["content"]

    if "visibility" in data:
        if data["visibility"] not in ["public", "private"]:
            return (
                jsonify(
                    {
                        "errors": [
                            {
                                "status": "400",
                                "title": "Invalid Visibility",
                                "detail": "Visibility must be either 'public' or 'private'",
                            }
                        ]
                    }
                ),
                400,
            )
        entry.visibility = data["visibility"]

    db.session.commit()

    return jsonify({"data": entry.to_jsonapi()}), 200


@api_bp.route("/entries/<string:entry_id>", methods=["DELETE"])
@require_auth
def delete_entry(current_scribe, entry_id):
    """Delete an entry.

    Scribes can only delete their own entries.

    Authentication:
        HTTP Basic Auth required

    Args:
        current_scribe: Authenticated scribe (from @require_auth)
        entry_id: The UUID of the entry to delete

    Returns:
        204 No Content: Entry deleted successfully
        403 Forbidden: Attempting to delete another scribe's entry
        404 Not Found: Entry does not exist

    Example:
        curl -X DELETE http://localhost:5000/api/entries/550e8400-e29b-41d4-a716-446655440000 \\
             -u alice:secret123 \\
             -i  # -i flag shows 204 status code
    """
    entry = db.session.get(Entry, entry_id)

    # Return 404 if entry doesn't exist
    if not entry:
        return (
            jsonify(
                {
                    "errors": [
                        {
                            "status": "404",
                            "title": "Entry Not Found",
                            "detail": f"No entry exists with ID {entry_id}",
                        }
                    ]
                }
            ),
            404,
        )

    # Check ownership - scribes can only delete their own entries
    if current_scribe.id != entry.scribe_id:
        return (
            jsonify(
                {
                    "errors": [
                        {
                            "status": "403",
                            "title": "Forbidden",
                            "detail": "You can only delete your own entries",
                        }
                    ]
                }
            ),
            403,
        )

    # Delete entry
    db.session.delete(entry)
    db.session.commit()

    # Return 204 No Content (empty response body)
    return "", 204


@api_bp.route("/chronicle", methods=["GET"])
@require_auth
def get_chronicle(current_scribe):
    """Get authenticated scribe's chronicle (all their entries).

    Returns all entries created by the authenticated scribe, ordered by
    creation date (newest first). Includes both public and private entries.

    Authentication:
        HTTP Basic Auth required

    Args:
        current_scribe: Authenticated scribe (from @require_auth)

    Returns:
        200 OK: Returns array of entries (may be empty)

    Example:
        curl -X GET http://localhost:5000/api/chronicle \\
             -u alice:secret123 \\
             -H "Accept: application/vnd.api+json"
    """
    # Get all entries for the authenticated scribe, ordered newest first
    entries = (
        Entry.query.filter_by(scribe_id=current_scribe.id)
        .order_by(Entry.created_at.desc())
        .all()
    )

    # Convert to JSON:API format
    entries_data = [entry.to_jsonapi() for entry in entries]

    return jsonify({"data": entries_data}), 200
