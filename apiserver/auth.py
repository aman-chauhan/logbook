"""Authentication utilities and decorators for Logbook API.

This module provides HTTP Basic Authentication decorators for securing API endpoints.
Uses Werkzeug's built-in Basic Auth support and SQLAlchemy for user verification.
"""

from functools import wraps
from flask import request, jsonify
from .models import Scribe


def require_auth(f):
    """Decorator to require HTTP Basic Authentication.

    Validates credentials against the Scribe database and passes the authenticated
    scribe as the first argument to the decorated function.

    Returns JSON:API formatted error responses for authentication failures:
    - 401 if credentials are missing or invalid

    Example:
        @api_bp.route('/protected')
        @require_auth
        def protected_route(current_scribe):
            return jsonify({'message': f'Hello {current_scribe.username}'})
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get Basic Auth credentials from request
        auth = request.authorization

        # Return 401 if no credentials provided
        if not auth:
            return (
                jsonify(
                    {
                        "errors": [
                            {
                                "status": "401",
                                "title": "Authentication Required",
                                "detail": "You must provide valid credentials to access this resource",
                            }
                        ]
                    }
                ),
                401,
            )

        # Look up scribe by username
        scribe = Scribe.query.filter_by(username=auth.username).first()

        # Return 401 if scribe not found or password incorrect
        if not scribe or not scribe.check_password(auth.password):
            return (
                jsonify(
                    {
                        "errors": [
                            {
                                "status": "401",
                                "title": "Invalid Credentials",
                                "detail": "The username or password provided is incorrect",
                            }
                        ]
                    }
                ),
                401,
            )

        # Pass authenticated scribe to the route function
        return f(scribe, *args, **kwargs)

    return decorated_function


def optional_auth(f):
    """Decorator for endpoints that work with or without authentication.

    If valid credentials are provided, passes the authenticated scribe to the function.
    If no credentials or invalid credentials, passes None instead.

    This is useful for endpoints like GET /entries/<id> where:
    - Public entries can be viewed by anyone (authenticated or not)
    - Private entries can only be viewed by the owner (requires authentication)

    Example:
        @api_bp.route('/entries/<int:entry_id>')
        @optional_auth
        def get_entry(current_scribe, entry_id):
            entry = Entry.query.get_or_404(entry_id)
            if entry.visibility == 'private' and (not current_scribe or current_scribe.id != entry.scribe_id):
                abort(404)  # Hide existence of private entries from non-owners
            return jsonify({'data': entry.to_jsonapi()})
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get Basic Auth credentials from request
        auth = request.authorization

        # If no credentials provided, pass None
        if not auth:
            return f(None, *args, **kwargs)

        # Look up scribe by username
        scribe = Scribe.query.filter_by(username=auth.username).first()

        # If credentials invalid, pass None (don't return error for optional auth)
        if not scribe or not scribe.check_password(auth.password):
            return f(None, *args, **kwargs)

        # Pass authenticated scribe to the route function
        return f(scribe, *args, **kwargs)

    return decorated_function
