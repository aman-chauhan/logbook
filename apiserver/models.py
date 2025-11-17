"""Database models for Logbook API.

This module defines the core database models for the Logbook platform:
- Scribe: User accounts with authentication
- Entry: Content entries in a scribe's chronicle
"""

from datetime import datetime
from typing import TYPE_CHECKING
from werkzeug.security import generate_password_hash, check_password_hash
from .extensions import db


class Scribe(db.Model):
    """Scribe account model.

    A Scribe is a user who documents their journey in Logbook.
    Stores authentication credentials and profile information.

    Password Security:
    - Uses Werkzeug's pbkdf2:sha256 with 260,000 iterations
    - Each password gets a unique randomly generated salt
    - Salt is embedded in password_hash: pbkdf2:sha256:260000$<salt>$<hash>
    - Salt length: 16 bytes (provides 128 bits of randomness)
    """

    __tablename__ = "scribes"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    bio = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    entries = db.relationship(
        "Entry", backref="scribe", lazy="dynamic", cascade="all, delete-orphan"
    )

    def set_password(self, password):
        """Hash and set the scribe's password.

        Uses pbkdf2:sha256 with a randomly generated 16-byte salt.
        The salt is embedded in the hash string stored in password_hash.

        Args:
            password (str): The plain text password to hash
        """
        self.password_hash = generate_password_hash(
            password, method="pbkdf2:sha256", salt_length=16
        )

    def check_password(self, password):
        """Verify password against stored hash.

        Extracts the salt from password_hash and verifies the password.

        Args:
            password (str): The plain text password to verify

        Returns:
            bool: True if password matches, False otherwise
        """
        return check_password_hash(self.password_hash, password)

    def to_jsonapi(self):
        """Return scribe data in JSON:API format.

        Returns a JSON:API resource object with type, id, and attributes.
        Follows JSON:API v1.1 specification.

        Returns:
            dict: JSON:API formatted resource object
        """
        return {
            "type": "scribes",
            "id": str(self.id),
            "attributes": {
                "username": self.username,
                "email": self.email,
                "bio": self.bio,
                "createdAt": self.created_at.isoformat() + "Z",
                "updatedAt": self.updated_at.isoformat() + "Z",
            },
        }

    def __repr__(self):
        return f"<Scribe {self.username}>"


class Entry(db.Model):
    """Entry model.

    An Entry represents a purposeful record in a Scribe's Chronicle.
    Stores content and visibility settings.

    Visibility Options:
    - 'public': Visible to all users
    - 'private': Visible only to the scribe who created it
    """

    __tablename__ = "entries"

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    visibility = db.Column(
        db.String(10), nullable=False, default="public"
    )  # 'public' or 'private'
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    scribe_id = db.Column(
        db.Integer, db.ForeignKey("scribes.id"), nullable=False, index=True
    )

    # Type hint for backref relationship (created by Scribe.entries relationship)
    if TYPE_CHECKING:
        scribe: "Scribe"

    def to_jsonapi(self):
        """Return entry data in JSON:API format.

        Returns a JSON:API resource object with type, id, and attributes.
        Follows JSON:API v1.1 specification.

        Returns:
            dict: JSON:API formatted resource object
        """
        return {
            "type": "entries",
            "id": str(self.id),
            "attributes": {
                "content": self.content,
                "visibility": self.visibility,
                "createdAt": self.created_at.isoformat() + "Z",
                "updatedAt": self.updated_at.isoformat() + "Z",
                "scribeId": self.scribe_id,
                "scribeUsername": self.scribe.username,
            },
        }

    def __repr__(self):
        return f"<Entry {self.id} by {self.scribe_id}>"
