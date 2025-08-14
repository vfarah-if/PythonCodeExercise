"""Unit tests for AWSAccount entity."""

import pytest

from src.setup_environment.domain.entities import AWSAccount


class TestAWSAccount:
    """Test suite for AWSAccount entity."""

    def test_create_aws_account_with_valid_data(self):
        """Test creating AWS account with valid data."""
        account = AWSAccount(
            name="dev",
            account_id="590184046376",
            email="test@webuild-ai.com",
            role="Engineer",
            is_default=True,
        )

        assert account.name == "dev"
        assert account.account_id == "590184046376"
        assert account.email == "test@webuild-ai.com"
        assert account.role == "Engineer"
        assert account.is_default is True

    def test_create_aws_account_with_defaults(self):
        """Test creating AWS account with default values."""
        account = AWSAccount(
            name="TestAccount",
            account_id="123456789012",
            email="test@example.com",
        )

        assert account.role == "Engineer"
        assert account.is_default is False

    def test_string_representation(self):
        """Test string representation of AWS account."""
        account = AWSAccount(
            name="TestAccount",
            account_id="123456789012",
            email="test@example.com",
        )

        assert str(account) == "TestAccount (123456789012)"

    def test_string_representation_with_default(self):
        """Test string representation of default AWS account."""
        account = AWSAccount(
            name="TestAccount",
            account_id="123456789012",
            email="test@example.com",
            is_default=True,
        )

        assert str(account) == "TestAccount (123456789012) [default]"

    def test_repr_representation(self):
        """Test repr representation of AWS account."""
        account = AWSAccount(
            name="TestAccount",
            account_id="123456789012",
            email="test@example.com",
            role="Admin",
            is_default=True,
        )

        expected = (
            "AWSAccount(name='TestAccount', account_id='123456789012', "
            "email='test@example.com', role='Admin', is_default=True)"
        )
        assert repr(account) == expected

    def test_to_dict(self):
        """Test converting AWS account to dictionary."""
        account = AWSAccount(
            name="TestAccount",
            account_id="123456789012",
            email="test@example.com",
            role="Admin",
            is_default=True,
        )

        expected = {
            "name": "TestAccount",
            "account_id": "123456789012",
            "email": "test@example.com",
            "role": "Admin",
            "is_default": True,
        }
        assert account.to_dict() == expected

    def test_from_dict_with_is_default(self):
        """Test creating AWS account from dictionary with is_default."""
        data = {
            "name": "TestAccount",
            "account_id": "123456789012",
            "email": "test@example.com",
            "role": "Admin",
            "is_default": True,
        }

        account = AWSAccount.from_dict(data)

        assert account.name == "TestAccount"
        assert account.account_id == "123456789012"
        assert account.email == "test@example.com"
        assert account.role == "Admin"
        assert account.is_default is True

    def test_from_dict_with_default_key(self):
        """Test creating AWS account from dictionary with 'default' key."""
        data = {
            "name": "TestAccount",
            "account_id": "123456789012",
            "email": "test@example.com",
            "role": "Admin",
            "default": True,
        }

        account = AWSAccount.from_dict(data)

        assert account.is_default is True

    def test_from_dict_with_missing_optional_fields(self):
        """Test creating AWS account from dictionary with missing optional fields."""
        data = {
            "name": "TestAccount",
            "account_id": "123456789012",
            "email": "test@example.com",
        }

        account = AWSAccount.from_dict(data)

        assert account.role == "Engineer"
        assert account.is_default is False

    def test_validation_empty_name(self):
        """Test validation fails for empty name."""
        with pytest.raises(ValueError, match="Account name cannot be empty"):
            AWSAccount(
                name="",
                account_id="123456789012",
                email="test@example.com",
            )

    def test_validation_whitespace_name(self):
        """Test validation fails for whitespace-only name."""
        with pytest.raises(ValueError, match="Account name cannot be empty"):
            AWSAccount(
                name="   ",
                account_id="123456789012",
                email="test@example.com",
            )

    def test_validation_empty_account_id(self):
        """Test validation fails for empty account ID."""
        with pytest.raises(ValueError, match="Account ID cannot be empty"):
            AWSAccount(
                name="TestAccount",
                account_id="",
                email="test@example.com",
            )

    def test_validation_invalid_account_id_not_digits(self):
        """Test validation fails for non-digit account ID."""
        with pytest.raises(
            ValueError, match="Invalid AWS account ID.*Must be a 12-digit number"
        ):
            AWSAccount(
                name="TestAccount",
                account_id="abc123456789",
                email="test@example.com",
            )

    def test_validation_invalid_account_id_wrong_length(self):
        """Test validation fails for wrong length account ID."""
        with pytest.raises(
            ValueError, match="Invalid AWS account ID.*Must be a 12-digit number"
        ):
            AWSAccount(
                name="TestAccount",
                account_id="12345",
                email="test@example.com",
            )

    def test_validation_empty_email(self):
        """Test validation fails for empty email."""
        with pytest.raises(ValueError, match="Email cannot be empty"):
            AWSAccount(
                name="TestAccount",
                account_id="123456789012",
                email="",
            )

    def test_validation_invalid_email_format(self):
        """Test validation fails for invalid email format."""
        with pytest.raises(ValueError, match="Invalid email format"):
            AWSAccount(
                name="TestAccount",
                account_id="123456789012",
                email="invalid-email",
            )

    def test_validation_empty_role(self):
        """Test validation fails for empty role."""
        with pytest.raises(ValueError, match="Role cannot be empty"):
            AWSAccount(
                name="TestAccount",
                account_id="123456789012",
                email="test@example.com",
                role="",
            )
