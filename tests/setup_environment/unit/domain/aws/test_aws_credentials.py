"""Unit tests for AWSCredentials entity."""

from datetime import datetime, timedelta

import pytest

from src.setup_environment.domain.entities import AWSCredentials


class TestAWSCredentials:
    """Test suite for AWSCredentials entity."""

    def test_create_aws_credentials_with_valid_data(self):
        """Test creating AWS credentials with valid data."""
        expiration = datetime.now() + timedelta(hours=12)
        credentials = AWSCredentials(
            access_key_id="ASIAEXAMPLE123456789",
            secret_access_key="test-secret-key",
            session_token="test-session-token",
            expiration=expiration,
            region="us-east-1",
        )

        assert credentials.access_key_id == "ASIAEXAMPLE123456789"
        assert credentials.secret_access_key == "test-secret-key"
        assert credentials.session_token == "test-session-token"
        assert credentials.expiration == expiration
        assert credentials.region == "us-east-1"

    def test_create_aws_credentials_with_default_region(self):
        """Test creating AWS credentials with default region."""
        expiration = datetime.now() + timedelta(hours=12)
        credentials = AWSCredentials(
            access_key_id="ASIAEXAMPLE123456789",
            secret_access_key="test-secret-key",
            session_token="test-session-token",
            expiration=expiration,
        )

        assert credentials.region == "eu-west-2"

    def test_is_expired_false_when_valid(self):
        """Test is_expired returns False when credentials are valid."""
        expiration = datetime.now() + timedelta(hours=1)
        credentials = AWSCredentials(
            access_key_id="ASIAEXAMPLE123456789",
            secret_access_key="test-secret-key",
            session_token="test-session-token",
            expiration=expiration,
        )

        assert credentials.is_expired() is False

    def test_is_expired_true_when_expired(self):
        """Test is_expired returns True when credentials are expired."""
        expiration = datetime.now() - timedelta(hours=1)
        credentials = AWSCredentials(
            access_key_id="ASIAEXAMPLE123456789",
            secret_access_key="test-secret-key",
            session_token="test-session-token",
            expiration=expiration,
        )

        assert credentials.is_expired() is True

    def test_time_until_expiry_minutes(self):
        """Test time_until_expiry returns minutes when less than 1 hour."""
        expiration = datetime.now() + timedelta(minutes=30)
        credentials = AWSCredentials(
            access_key_id="ASIAEXAMPLE123456789",
            secret_access_key="test-secret-key",
            session_token="test-session-token",
            expiration=expiration,
        )

        result = credentials.time_until_expiry()
        assert "30 minutes" in result or "29 minutes" in result  # Account for timing

    def test_time_until_expiry_hours(self):
        """Test time_until_expiry returns hours when more than 1 hour."""
        expiration = datetime.now() + timedelta(hours=6)
        credentials = AWSCredentials(
            access_key_id="ASIAEXAMPLE123456789",
            secret_access_key="test-secret-key",
            session_token="test-session-token",
            expiration=expiration,
        )

        result = credentials.time_until_expiry()
        assert "6 hours" in result or "5 hours" in result  # Account for timing

    def test_time_until_expiry_days(self):
        """Test time_until_expiry returns days when more than 24 hours."""
        expiration = datetime.now() + timedelta(days=2)
        credentials = AWSCredentials(
            access_key_id="ASIAEXAMPLE123456789",
            secret_access_key="test-secret-key",
            session_token="test-session-token",
            expiration=expiration,
        )

        result = credentials.time_until_expiry()
        assert "2 days" in result or "1 days" in result  # Account for timing

    def test_time_until_expiry_expired(self):
        """Test time_until_expiry returns 'Expired' when credentials are expired."""
        expiration = datetime.now() - timedelta(hours=1)
        credentials = AWSCredentials(
            access_key_id="ASIAEXAMPLE123456789",
            secret_access_key="test-secret-key",
            session_token="test-session-token",
            expiration=expiration,
        )

        assert credentials.time_until_expiry() == "Expired"

    def test_to_env_vars_bash_format(self):
        """Test exporting credentials as bash environment variables."""
        expiration = datetime.now() + timedelta(hours=12)
        credentials = AWSCredentials(
            access_key_id="ASIAEXAMPLE123456789",
            secret_access_key="test-secret-key",
            session_token="test-session-token",
            expiration=expiration,
            region="us-east-1",
        )

        result = credentials.to_env_vars("bash")

        expected_lines = [
            'export AWS_ACCESS_KEY_ID="ASIAEXAMPLE123456789"',
            'export AWS_SECRET_ACCESS_KEY="test-secret-key"',
            'export AWS_SESSION_TOKEN="test-session-token"',
            'export AWS_DEFAULT_REGION="us-east-1"',
        ]

        for line in expected_lines:
            assert line in result

    def test_to_env_vars_zsh_format(self):
        """Test exporting credentials as zsh environment variables."""
        expiration = datetime.now() + timedelta(hours=12)
        credentials = AWSCredentials(
            access_key_id="ASIAEXAMPLE123456789",
            secret_access_key="test-secret-key",
            session_token="test-session-token",
            expiration=expiration,
            region="us-east-1",
        )

        result = credentials.to_env_vars("zsh")

        # zsh uses same format as bash
        expected_lines = [
            'export AWS_ACCESS_KEY_ID="ASIAEXAMPLE123456789"',
            'export AWS_SECRET_ACCESS_KEY="test-secret-key"',
            'export AWS_SESSION_TOKEN="test-session-token"',
            'export AWS_DEFAULT_REGION="us-east-1"',
        ]

        for line in expected_lines:
            assert line in result

    def test_to_env_vars_fish_format(self):
        """Test exporting credentials as fish shell environment variables."""
        expiration = datetime.now() + timedelta(hours=12)
        credentials = AWSCredentials(
            access_key_id="ASIAEXAMPLE123456789",
            secret_access_key="test-secret-key",
            session_token="test-session-token",
            expiration=expiration,
            region="us-east-1",
        )

        result = credentials.to_env_vars("fish")

        expected_lines = [
            'set -x AWS_ACCESS_KEY_ID "ASIAEXAMPLE123456789"',
            'set -x AWS_SECRET_ACCESS_KEY "test-secret-key"',
            'set -x AWS_SESSION_TOKEN "test-session-token"',
            'set -x AWS_DEFAULT_REGION "us-east-1"',
        ]

        for line in expected_lines:
            assert line in result

    def test_to_env_vars_powershell_format(self):
        """Test exporting credentials as PowerShell environment variables."""
        expiration = datetime.now() + timedelta(hours=12)
        credentials = AWSCredentials(
            access_key_id="ASIAEXAMPLE123456789",
            secret_access_key="test-secret-key",
            session_token="test-session-token",
            expiration=expiration,
            region="us-east-1",
        )

        result = credentials.to_env_vars("powershell")

        expected_lines = [
            '$env:AWS_ACCESS_KEY_ID="ASIAEXAMPLE123456789"',
            '$env:AWS_SECRET_ACCESS_KEY="test-secret-key"',
            '$env:AWS_SESSION_TOKEN="test-session-token"',
            '$env:AWS_DEFAULT_REGION="us-east-1"',
        ]

        for line in expected_lines:
            assert line in result

    def test_to_env_vars_unsupported_format(self):
        """Test exporting credentials with unsupported format raises error."""
        expiration = datetime.now() + timedelta(hours=12)
        credentials = AWSCredentials(
            access_key_id="ASIAEXAMPLE123456789",
            secret_access_key="test-secret-key",
            session_token="test-session-token",
            expiration=expiration,
        )

        with pytest.raises(ValueError, match="Unsupported shell format: unsupported"):
            credentials.to_env_vars("unsupported")

    def test_to_aws_config_format_default_profile(self):
        """Test exporting credentials in AWS config format with default profile."""
        expiration = datetime.now() + timedelta(hours=12)
        credentials = AWSCredentials(
            access_key_id="ASIAEXAMPLE123456789",
            secret_access_key="test-secret-key",
            session_token="test-session-token",
            expiration=expiration,
            region="us-east-1",
        )

        result = credentials.to_aws_config_format()

        expected_lines = [
            "[default]",
            "aws_access_key_id = ASIAEXAMPLE123456789",
            "aws_secret_access_key = test-secret-key",
            "aws_session_token = test-session-token",
            "region = us-east-1",
        ]

        for line in expected_lines:
            assert line in result

    def test_to_aws_config_format_custom_profile(self):
        """Test exporting credentials in AWS config format with custom profile."""
        expiration = datetime.now() + timedelta(hours=12)
        credentials = AWSCredentials(
            access_key_id="ASIAEXAMPLE123456789",
            secret_access_key="test-secret-key",
            session_token="test-session-token",
            expiration=expiration,
            region="us-east-1",
        )

        result = credentials.to_aws_config_format("my-profile")

        assert "[my-profile]" in result

    def test_mask_sensitive_data(self):
        """Test masking sensitive data for logging."""
        expiration = datetime.now() + timedelta(hours=12)
        credentials = AWSCredentials(
            access_key_id="ASIAEXAMPLE123456789",
            secret_access_key="test-secret-key-that-is-very-long",
            session_token="test-session-token-that-is-very-long-for-testing",
            expiration=expiration,
            region="us-east-1",
        )

        masked = credentials.mask_sensitive_data()

        assert masked["access_key_id"] == "ASIAEXAM...6789"
        assert masked["secret_access_key"] == "***MASKED***"
        assert masked["session_token"] == "test-session-token-t...or-testing"
        assert masked["expiration"] == expiration.isoformat()
        assert masked["region"] == "us-east-1"

    def test_validation_empty_access_key_id(self):
        """Test validation fails for empty access key ID."""
        expiration = datetime.now() + timedelta(hours=12)

        with pytest.raises(ValueError, match="Access key ID cannot be empty"):
            AWSCredentials(
                access_key_id="",
                secret_access_key="test-secret-key",
                session_token="test-session-token",
                expiration=expiration,
            )

    def test_validation_empty_secret_access_key(self):
        """Test validation fails for empty secret access key."""
        expiration = datetime.now() + timedelta(hours=12)

        with pytest.raises(ValueError, match="Secret access key cannot be empty"):
            AWSCredentials(
                access_key_id="ASIAEXAMPLE123456789",
                secret_access_key="",
                session_token="test-session-token",
                expiration=expiration,
            )

    def test_validation_empty_session_token(self):
        """Test validation fails for empty session token."""
        expiration = datetime.now() + timedelta(hours=12)

        with pytest.raises(ValueError, match="Session token cannot be empty"):
            AWSCredentials(
                access_key_id="ASIAEXAMPLE123456789",
                secret_access_key="test-secret-key",
                session_token="",
                expiration=expiration,
            )

    def test_validation_invalid_expiration_type(self):
        """Test validation fails for invalid expiration type."""
        with pytest.raises(TypeError, match="Expiration must be a datetime object"):
            AWSCredentials(
                access_key_id="ASIAEXAMPLE123456789",
                secret_access_key="test-secret-key",
                session_token="test-session-token",
                expiration="not-a-datetime",
            )

    def test_validation_empty_region(self):
        """Test validation fails for empty region."""
        expiration = datetime.now() + timedelta(hours=12)

        with pytest.raises(ValueError, match="Region cannot be empty"):
            AWSCredentials(
                access_key_id="ASIAEXAMPLE123456789",
                secret_access_key="test-secret-key",
                session_token="test-session-token",
                expiration=expiration,
                region="",
            )

    def test_validation_invalid_access_key_format(self):
        """Test validation fails for invalid access key format."""
        expiration = datetime.now() + timedelta(hours=12)

        with pytest.raises(
            ValueError,
            match="Invalid access key ID format.*AWS access keys should start with ASIA or AKIA",
        ):
            AWSCredentials(
                access_key_id="INVALID123456789",
                secret_access_key="test-secret-key",
                session_token="test-session-token",
                expiration=expiration,
            )
