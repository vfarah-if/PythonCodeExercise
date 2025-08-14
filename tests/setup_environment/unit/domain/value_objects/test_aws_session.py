"""Unit tests for AWSSession value object."""

from datetime import datetime, timedelta

import pytest

from src.setup_environment.domain.value_objects import AWSSession


class TestAWSSession:
    """Test suite for AWSSession value object."""

    def test_create_aws_session_with_valid_data(self):
        """Test creating AWS session with valid data."""
        expires_at = datetime.now() + timedelta(hours=12)
        session = AWSSession(
            access_token="test-access-token",
            expires_at=expires_at,
            region="eu-west-2",
        )

        assert session.access_token == "test-access-token"
        assert session.expires_at == expires_at
        assert session.region == "eu-west-2"

    def test_create_aws_session_with_default_region(self):
        """Test creating AWS session with default region."""
        expires_at = datetime.now() + timedelta(hours=12)
        session = AWSSession(
            access_token="test-access-token",
            expires_at=expires_at,
        )

        assert session.region == "eu-west-2"

    def test_is_expired_false_when_valid(self):
        """Test is_expired returns False when session is valid."""
        expires_at = datetime.now() + timedelta(hours=1)
        session = AWSSession(
            access_token="test-access-token",
            expires_at=expires_at,
        )

        assert session.is_expired() is False

    def test_is_expired_true_when_expired(self):
        """Test is_expired returns True when session is expired."""
        expires_at = datetime.now() - timedelta(hours=1)
        session = AWSSession(
            access_token="test-access-token",
            expires_at=expires_at,
        )

        assert session.is_expired() is True

    def test_time_until_expiry_minutes(self):
        """Test time_remaining returns minutes when less than 1 hour."""
        expires_at = datetime.now() + timedelta(minutes=45)
        session = AWSSession(
            access_token="test-access-token",
            expires_at=expires_at,
        )

        result = session.time_remaining()
        assert "45 minutes" in result or "44 minutes" in result  # Account for timing

    def test_time_until_expiry_hours(self):
        """Test time_remaining returns hours when more than 1 hour."""
        expires_at = datetime.now() + timedelta(hours=8)
        session = AWSSession(
            access_token="test-access-token",
            expires_at=expires_at,
        )

        result = session.time_remaining()
        assert "8 hours" in result or "7 hours" in result  # Account for timing

    def test_time_until_expiry_expired(self):
        """Test time_remaining returns 'Expired' when session is expired."""
        expires_at = datetime.now() - timedelta(hours=1)
        session = AWSSession(
            access_token="test-access-token",
            expires_at=expires_at,
        )

        assert session.time_remaining() == "Expired"

    def test_equality(self):
        """Test equality comparison of AWS sessions."""
        expires_at = datetime.now() + timedelta(hours=12)
        session1 = AWSSession(
            access_token="test-access-token",
            expires_at=expires_at,
            region="eu-west-2",
        )
        session2 = AWSSession(
            access_token="test-access-token",
            expires_at=expires_at,
            region="eu-west-2",
        )

        assert session1 == session2

    def test_inequality(self):
        """Test inequality comparison of AWS sessions."""
        expires_at = datetime.now() + timedelta(hours=12)
        session1 = AWSSession(
            access_token="test-access-token-1",
            expires_at=expires_at,
        )
        session2 = AWSSession(
            access_token="test-access-token-2",
            expires_at=expires_at,
        )

        assert session1 != session2

    def test_hash_equality(self):
        """Test hash equality for sessions with same values."""
        expires_at = datetime.now() + timedelta(hours=12)
        session1 = AWSSession(
            access_token="test-access-token",
            expires_at=expires_at,
        )
        session2 = AWSSession(
            access_token="test-access-token",
            expires_at=expires_at,
        )

        assert hash(session1) == hash(session2)

    def test_to_dict(self):
        """Test converting AWS session to dictionary."""
        expires_at = datetime.now() + timedelta(hours=12)
        session = AWSSession(
            access_token="test-access-token",
            expires_at=expires_at,
            region="us-east-1",
        )

        result = session.to_dict()
        assert result["access_token"] == "***MASKED***"  # short token gets masked
        assert result["expires_at"] == expires_at.isoformat()
        assert result["region"] == "us-east-1"
        assert "is_valid" in result

    def test_create_from_constructor(self):
        """Test creating AWS session from constructor."""
        expires_at = datetime.now() + timedelta(hours=12)
        session = AWSSession(
            access_token="test-access-token",
            expires_at=expires_at,
            region="us-east-1",
        )

        assert session.access_token == "test-access-token"
        assert session.expires_at == expires_at
        assert session.region == "us-east-1"

    def test_create_with_missing_optional_fields(self):
        """Test creating AWS session with missing optional fields."""
        expires_at = datetime.now() + timedelta(hours=12)
        session = AWSSession(
            access_token="test-access-token",
            expires_at=expires_at,
        )

        assert session.region == "eu-west-2"

    def test_mask_access_token(self):
        """Test masking access token for logging."""
        expires_at = datetime.now() + timedelta(hours=12)
        session = AWSSession(
            access_token="this-is-a-very-long-access-token-for-testing",
            expires_at=expires_at,
        )

        masked = session.masked_token()

        assert masked == "this-is-a-...or-testing"

    def test_mask_short_access_token(self):
        """Test masking short access token for logging."""
        expires_at = datetime.now() + timedelta(hours=12)
        session = AWSSession(
            access_token="short",
            expires_at=expires_at,
        )

        masked = session.masked_token()

        assert masked == "***MASKED***"

    def test_validation_empty_access_token(self):
        """Test validation fails for empty access token."""
        expires_at = datetime.now() + timedelta(hours=12)

        with pytest.raises(ValueError, match="Access token cannot be empty"):
            AWSSession(
                access_token="",
                expires_at=expires_at,
            )

    def test_validation_whitespace_access_token(self):
        """Test validation fails for whitespace-only access token."""
        expires_at = datetime.now() + timedelta(hours=12)

        with pytest.raises(ValueError, match="Access token cannot be empty"):
            AWSSession(
                access_token="   ",
                expires_at=expires_at,
            )

    def test_validation_invalid_expires_at_type(self):
        """Test validation fails for invalid expires_at type."""
        with pytest.raises(TypeError, match="expires_at must be a datetime object"):
            AWSSession(
                access_token="test-access-token",
                expires_at="not-a-datetime",
            )

    def test_validation_empty_region(self):
        """Test validation fails for empty region."""
        expires_at = datetime.now() + timedelta(hours=12)

        with pytest.raises(ValueError, match="Region cannot be empty"):
            AWSSession(
                access_token="test-access-token",
                expires_at=expires_at,
                region="",
            )

    def test_repr_representation(self):
        """Test repr representation of AWS session."""
        expires_at = datetime.now() + timedelta(hours=12)
        session = AWSSession(
            access_token="test-access-token",
            expires_at=expires_at,
            region="us-east-1",
        )

        result = repr(session)
        assert "AWSSession" in result
        assert "access_token" in result
        assert "expires_at" in result
        assert "region" in result

    def test_str_representation(self):
        """Test string representation of AWS session."""
        expires_at = datetime.now() + timedelta(hours=12)
        session = AWSSession(
            access_token="test-access-token",
            expires_at=expires_at,
            region="us-east-1",
        )

        result = str(session)
        assert "AWSSession" in result or "AWS" in result
