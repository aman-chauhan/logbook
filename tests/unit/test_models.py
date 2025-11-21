"""Unit tests for database models.

Tests for Scribe and Entry models including:
- Model initialization
- Password hashing and verification
- JSON:API serialization
- Relationships
- Model validation
"""

import pytest
from datetime import datetime
from apiserver.models import Scribe, Entry


class TestScribeModel:
    """Test suite for Scribe model."""

    @pytest.mark.unit
    def test_scribe_creation(self, db, faker):
        """Test creating a new scribe."""
        username = faker.user_name()
        email = faker.email()
        bio = faker.sentence()

        scribe = Scribe(username=username, email=email, bio=bio)
        scribe.set_password("testpass")
        db.session.add(scribe)
        db.session.commit()

        assert scribe.id is not None
        assert scribe.username == username
        assert scribe.email == email
        assert scribe.bio == bio
        assert scribe.created_at is not None
        assert scribe.updated_at is not None
        assert isinstance(scribe.created_at, datetime)
        assert isinstance(scribe.updated_at, datetime)

    @pytest.mark.unit
    def test_scribe_creation_without_bio(self, db, faker):
        """Test creating a scribe without bio (optional field)."""
        username = faker.user_name()
        email = faker.email()

        scribe = Scribe(username=username, email=email)
        scribe.set_password("testpass")
        db.session.add(scribe)
        db.session.commit()

        assert scribe.id is not None
        assert scribe.username == username
        assert scribe.email == email
        assert scribe.bio is None

    @pytest.mark.unit
    def test_scribe_username_unique_constraint(self, db, sample_scribe, faker):
        """Test that username must be unique."""
        from sqlalchemy.exc import IntegrityError

        # Try to create scribe with duplicate username
        duplicate = Scribe(username=sample_scribe.username, email=faker.email())
        duplicate.set_password("testpass")
        db.session.add(duplicate)

        with pytest.raises(IntegrityError):
            db.session.commit()

    @pytest.mark.unit
    def test_scribe_email_unique_constraint(self, db, sample_scribe, faker):
        """Test that email must be unique."""
        from sqlalchemy.exc import IntegrityError

        # Try to create scribe with duplicate email
        duplicate = Scribe(username=faker.user_name(), email=sample_scribe.email)
        duplicate.set_password("testpass")
        db.session.add(duplicate)

        with pytest.raises(IntegrityError):
            db.session.commit()

    @pytest.mark.unit
    def test_set_password(self, db, faker):
        """Test password hashing."""
        scribe = Scribe(username=faker.user_name(), email=faker.email())
        password = faker.password()
        scribe.set_password(password)

        assert scribe.password_hash is not None
        assert scribe.password_hash != password

    @pytest.mark.unit
    def test_check_password_correct(self, db, faker):
        """Test password verification with correct password."""
        scribe = Scribe(username=faker.user_name(), email=faker.email())
        password = faker.password()
        scribe.set_password(password)
        db.session.add(scribe)
        db.session.commit()

        assert scribe.check_password(password) is True

    @pytest.mark.unit
    def test_check_password_incorrect(self, db, faker):
        """Test password verification with incorrect password."""
        scribe = Scribe(username=faker.user_name(), email=faker.email())
        correct_password = faker.password()
        wrong_password = faker.password()
        scribe.set_password(correct_password)
        db.session.add(scribe)
        db.session.commit()

        assert scribe.check_password(wrong_password) is False

    @pytest.mark.unit
    def test_password_salt_is_unique(self, db, faker):
        """Test that each password gets a unique salt."""
        same_password = faker.password()

        scribe1 = Scribe(username=faker.user_name(), email=faker.email())
        scribe1.set_password(same_password)

        scribe2 = Scribe(username=faker.user_name(), email=faker.email())
        scribe2.set_password(same_password)

        # Same password should produce different hashes due to different salts
        assert scribe1.password_hash != scribe2.password_hash

    @pytest.mark.unit
    def test_scribe_to_jsonapi(self, db, sample_scribe):
        """Test JSON:API serialization."""
        result = sample_scribe.to_jsonapi()

        assert result["type"] == "scribes"
        assert result["id"] == str(sample_scribe.id)
        assert "attributes" in result

        attrs = result["attributes"]
        assert attrs["username"] == sample_scribe.username
        assert attrs["email"] == sample_scribe.email
        assert "createdAt" in attrs
        assert "updatedAt" in attrs
        assert attrs["createdAt"].endswith("Z")  # ISO format with Z
        assert attrs["updatedAt"].endswith("Z")

    @pytest.mark.unit
    def test_scribe_to_jsonapi_no_password(self, db, sample_scribe):
        """Test that password_hash is not included in JSON:API output."""
        result = sample_scribe.to_jsonapi()

        # Check that password is not in the serialized output
        assert "password" not in result["attributes"]
        assert "password_hash" not in result["attributes"]
        assert "passwordHash" not in result["attributes"]

    @pytest.mark.unit
    def test_scribe_repr(self, db, sample_scribe):
        """Test string representation of Scribe."""
        assert repr(sample_scribe) == f"<Scribe {sample_scribe.username}>"

    @pytest.mark.unit
    def test_scribe_entries_relationship(self, db, sample_scribe, entry_factory):
        """Test relationship between Scribe and Entry."""
        # Create entries for the scribe
        entry1 = entry_factory(scribe_id=sample_scribe.id)
        entry2 = entry_factory(scribe_id=sample_scribe.id)

        # Test relationship
        assert sample_scribe.entries.count() == 2
        assert entry1 in sample_scribe.entries.all()
        assert entry2 in sample_scribe.entries.all()

    @pytest.mark.unit
    def test_scribe_cascade_delete(self, db, sample_scribe, entry_factory):
        """Test that deleting a scribe deletes their entries (cascade)."""
        # Create entries for the scribe
        entry1 = entry_factory(scribe_id=sample_scribe.id)
        entry2 = entry_factory(scribe_id=sample_scribe.id)

        entry1_id = entry1.id
        entry2_id = entry2.id

        # Delete scribe
        db.session.delete(sample_scribe)
        db.session.commit()

        # Verify entries are also deleted
        assert db.session.get(Entry, entry1_id) is None
        assert db.session.get(Entry, entry2_id) is None


class TestEntryModel:
    """Test suite for Entry model."""

    @pytest.mark.unit
    def test_entry_creation_public(self, db, sample_scribe, faker):
        """Test creating a public entry."""
        content = faker.text(max_nb_chars=200)

        entry = Entry(
            content=content,
            scribe_id=sample_scribe.id,
            visibility="public"
        )
        db.session.add(entry)
        db.session.commit()

        assert entry.id is not None
        assert entry.content == content
        assert entry.scribe_id == sample_scribe.id
        assert entry.visibility == "public"
        assert entry.created_at is not None
        assert entry.updated_at is not None
        assert isinstance(entry.created_at, datetime)
        assert isinstance(entry.updated_at, datetime)

    @pytest.mark.unit
    def test_entry_creation_private(self, db, sample_scribe, faker):
        """Test creating a private entry."""
        content = faker.text(max_nb_chars=200)

        entry = Entry(
            content=content,
            scribe_id=sample_scribe.id,
            visibility="private"
        )
        db.session.add(entry)
        db.session.commit()

        assert entry.visibility == "private"

    @pytest.mark.unit
    def test_entry_default_visibility(self, db, sample_scribe, faker):
        """Test default visibility is public."""
        entry = Entry(content=faker.text(), scribe_id=sample_scribe.id)
        db.session.add(entry)
        db.session.commit()

        assert entry.visibility == "public"

    @pytest.mark.unit
    def test_entry_scribe_relationship(self, db, sample_scribe, faker):
        """Test backref relationship from Entry to Scribe."""
        entry = Entry(content=faker.text(), scribe_id=sample_scribe.id)
        db.session.add(entry)
        db.session.commit()

        # Test backref
        assert entry.scribe == sample_scribe
        assert entry.scribe.username == sample_scribe.username

    @pytest.mark.unit
    def test_entry_to_jsonapi(self, db, sample_scribe, faker):
        """Test JSON:API serialization."""
        content = faker.text(max_nb_chars=200)

        entry = Entry(
            content=content,
            scribe_id=sample_scribe.id,
            visibility="public"
        )
        db.session.add(entry)
        db.session.commit()

        result = entry.to_jsonapi()

        assert result["type"] == "entries"
        assert result["id"] == str(entry.id)
        assert "attributes" in result

        attrs = result["attributes"]
        assert attrs["content"] == content
        assert attrs["visibility"] == "public"
        assert attrs["scribeId"] == sample_scribe.id
        assert attrs["scribeUsername"] == sample_scribe.username
        assert "createdAt" in attrs
        assert "updatedAt" in attrs
        assert attrs["createdAt"].endswith("Z")
        assert attrs["updatedAt"].endswith("Z")

    @pytest.mark.unit
    def test_entry_repr(self, db, sample_entry):
        """Test string representation of Entry."""
        expected = f"<Entry {sample_entry.id} by {sample_entry.scribe_id}>"
        assert repr(sample_entry) == expected

    @pytest.mark.unit
    def test_entry_updated_at_field(self, db, sample_entry):
        """Test that updated_at field exists and can be modified.

        Note: SQLite in-memory databases don't reliably trigger automatic
        timestamp updates on UPDATE operations, so we test explicit updates.
        """
        from datetime import datetime

        # Verify updated_at exists and is a datetime
        assert isinstance(sample_entry.updated_at, datetime)

        # Test that we can explicitly update the timestamp
        # Use naive datetime to match what SQLite stores
        new_timestamp = datetime.utcnow()
        sample_entry.updated_at = new_timestamp
        sample_entry.content = "Updated content"
        db.session.commit()
        db.session.refresh(sample_entry)

        # Verify the field was updated
        assert sample_entry.updated_at == new_timestamp
        assert sample_entry.content == "Updated content"

    @pytest.mark.unit
    def test_entry_requires_content(self, db, sample_scribe):
        """Test that content is required."""
        from sqlalchemy.exc import IntegrityError

        entry = Entry(content=None, scribe_id=sample_scribe.id)
        db.session.add(entry)

        with pytest.raises(IntegrityError):
            db.session.commit()

    @pytest.mark.unit
    def test_entry_requires_scribe_id(self, db, faker):
        """Test that scribe_id is required."""
        from sqlalchemy.exc import IntegrityError

        entry = Entry(content=faker.text(), scribe_id=None)
        db.session.add(entry)

        with pytest.raises(IntegrityError):
            db.session.commit()

    @pytest.mark.unit
    def test_entry_foreign_key_constraint(self, db, faker):
        """Test that scribe_id must reference an existing scribe.

        This test verifies that foreign key constraints are properly enforced.
        """
        from sqlalchemy.exc import IntegrityError

        # Try to create entry with non-existent scribe_id (fake UUID)
        entry = Entry(content=faker.text(), scribe_id=faker.uuid4())
        db.session.add(entry)

        # Should raise IntegrityError due to foreign key constraint
        with pytest.raises(IntegrityError):
            db.session.commit()

    @pytest.mark.unit
    def test_multiple_entries_same_scribe(self, db, sample_scribe, entry_factory):
        """Test that a scribe can have multiple entries."""
        entries = [entry_factory(scribe_id=sample_scribe.id) for _ in range(5)]

        assert sample_scribe.entries.count() == 5
        for entry in entries:
            assert entry in sample_scribe.entries.all()
