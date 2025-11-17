"""API blueprint for Logbook.

This module creates and configures the main API blueprint that groups all
API endpoints under the /api prefix.

All endpoints follow the JSON:API v1.1 specification for consistent responses.
"""

from flask import Blueprint

# Create API blueprint
api_bp = Blueprint("api", __name__)

# Import routes to register them with the blueprint
# This must be done after creating the blueprint to avoid circular imports
from . import auth
