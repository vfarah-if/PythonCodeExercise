"""
Tests for Domain Layer
Tests entities, value objects, and domain logic.
These tests should have NO dependencies on external systems.
"""

from datetime import datetime

import pytest

from src.clean_architecture_example.domain.entities.user import User
from src.clean_architecture_example.domain.value_objects.email import Email


class TestEmailValueObject:
    """Test Email value object behaviour."""

    def test_valid_email_creation(self):
        """Test creating valid email addresses."""
        email = Email("test@example.com")
        assert email.value == "test@example.com"
        assert str(email) == "test@example.com"

    def test_email_normalisation(self):
        """Test email is converted to lowercase."""
        email = Email("Test@EXAMPLE.COM")
        assert email.value == "test@example.com"

    def test_email_domain_extraction(self):
        """Test domain property extracts correct domain."""
        email = Email("user@example.co.uk")
        assert email.domain == "example.co.uk"

    def test_email_local_part_extraction(self):
        """Test local_part property extracts correct part."""
        email = Email("john.doe@example.com")
        assert email.local_part == "john.doe"

    def test_empty_email_raises_error(self):
        """Test empty email raises ValueError."""
        with pytest.raises(ValueError, match="Email cannot be empty"):
            Email("")

    def test_invalid_email_format_raises_error(self):
        """Test invalid email format raises ValueError."""
        invalid_emails = ["invalid", "@example.com", "user@", "user space@example.com"]

        for invalid_email in invalid_emails:
            with pytest.raises(ValueError, match="Invalid email format"):
                Email(invalid_email)

    def test_email_equality(self):
        """Test email equality is based on value."""
        email1 = Email("test@example.com")
        email2 = Email("TEST@EXAMPLE.COM")  # Different case
        email3 = Email("other@example.com")

        assert email1 == email2  # Should be equal (both normalised)
        assert email1 != email3

    def test_email_immutability(self):
        """Test email is immutable (frozen dataclass)."""
        email = Email("test@example.com")

        with pytest.raises(AttributeError):
            email.value = "changed@example.com"


class TestUserEntity:
    """Test User entity behaviour."""

    def test_user_creation_with_valid_data(self):
        """Test creating user with valid data."""
        email = Email("john@example.com")
        user = User(email=email, first_name="John", last_name="Doe")

        assert user.email == email
        assert user.first_name == "John"
        assert user.last_name == "Doe"
        assert user.is_active is True
        assert user.id is not None
        assert len(user.id) > 0
        assert isinstance(user.created_at, datetime)

    def test_user_auto_generates_id(self):
        """Test user automatically generates unique ID."""
        email = Email("test@example.com")
        user1 = User(email=email, first_name="Test", last_name="User")
        user2 = User(email=email, first_name="Test", last_name="User")

        assert user1.id != user2.id
        assert len(user1.id) > 0
        assert len(user2.id) > 0

    def test_user_full_name_property(self):
        """Test full_name computed property."""
        email = Email("jane@example.com")
        user = User(email=email, first_name="Jane", last_name="Smith")

        assert user.full_name == "Jane Smith"

    def test_user_display_name_property(self):
        """Test display_name computed property."""
        email = Email("bob@example.com")
        user = User(email=email, first_name="Bob", last_name="Wilson")

        expected = "Bob Wilson (bob@example.com)"
        assert user.display_name == expected

    def test_empty_first_name_raises_error(self):
        """Test empty first name raises ValueError."""
        email = Email("test@example.com")

        with pytest.raises(ValueError, match="First name cannot be empty"):
            User(email=email, first_name="", last_name="Doe")

        with pytest.raises(ValueError, match="First name cannot be empty"):
            User(email=email, first_name="   ", last_name="Doe")

    def test_empty_last_name_raises_error(self):
        """Test empty last name raises ValueError."""
        email = Email("test@example.com")

        with pytest.raises(ValueError, match="Last name cannot be empty"):
            User(email=email, first_name="John", last_name="")

    def test_update_name_with_valid_data(self):
        """Test updating name with valid data."""
        email = Email("john@example.com")
        user = User(email=email, first_name="John", last_name="Doe")
        original_updated_at = user.updated_at

        user.update_name("Johnny", "Smith")

        assert user.first_name == "Johnny"
        assert user.last_name == "Smith"
        assert user.full_name == "Johnny Smith"
        assert user.updated_at is not None
        assert user.updated_at != original_updated_at

    def test_update_name_with_invalid_data_rolls_back(self):
        """Test updating name with invalid data rolls back changes."""
        email = Email("john@example.com")
        user = User(email=email, first_name="John", last_name="Doe")

        with pytest.raises(ValueError, match="First name cannot be empty"):
            user.update_name("", "Smith")

        # Should roll back to original values
        assert user.first_name == "John"
        assert user.last_name == "Doe"

    def test_user_deactivation(self):
        """Test user deactivation."""
        email = Email("active@example.com")
        user = User(email=email, first_name="Active", last_name="User")

        assert user.is_active is True

        user.deactivate()

        assert user.is_active is False
        assert user.updated_at is not None

    def test_deactivating_inactive_user_raises_error(self):
        """Test deactivating already inactive user raises error."""
        email = Email("inactive@example.com")
        user = User(email=email, first_name="Inactive", last_name="User")
        user.deactivate()  # First deactivation

        with pytest.raises(ValueError, match="User is already inactive"):
            user.deactivate()  # Second deactivation should fail

    def test_user_activation(self):
        """Test user activation."""
        email = Email("inactive@example.com")
        user = User(email=email, first_name="Inactive", last_name="User")
        user.deactivate()  # Make inactive first

        user.activate()

        assert user.is_active is True
        assert user.updated_at is not None

    def test_activating_active_user_raises_error(self):
        """Test activating already active user raises error."""
        email = Email("active@example.com")
        user = User(email=email, first_name="Active", last_name="User")

        with pytest.raises(ValueError, match="User is already active"):
            user.activate()

    def test_user_equality_based_on_id(self):
        """Test user equality is based on ID, not other attributes."""
        email1 = Email("user1@example.com")
        email2 = Email("user2@example.com")

        user1 = User(email=email1, first_name="User", last_name="One")
        user2 = User(email=email2, first_name="User", last_name="Two")
        user1_copy = User(email=email1, first_name="Different", last_name="Name")

        # Set same ID for user1_copy
        object.__setattr__(user1_copy, "id", user1.id)

        assert user1 != user2  # Different IDs
        assert user1 == user1_copy  # Same ID, different data

    def test_user_hash_based_on_id(self):
        """Test user hash is based on ID for use in sets/dicts."""
        email = Email("test@example.com")
        user1 = User(email=email, first_name="Test", last_name="User")
        user2 = User(email=email, first_name="Test", last_name="User")

        # Different users should have different hashes
        assert hash(user1) != hash(user2)

        # Same user should have consistent hash
        assert hash(user1) == hash(user1)

    def test_user_repr(self):
        """Test user string representation."""
        email = Email("repr@example.com")
        user = User(email=email, first_name="Repr", last_name="Test")

        repr_str = repr(user)
        assert "User(" in repr_str
        assert user.id in repr_str
        assert "repr@example.com" in repr_str
        assert "Repr Test" in repr_str
