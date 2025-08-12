"""Simple unit tests for SetupAWSCredentialsUseCase."""

from datetime import datetime, timedelta
from unittest.mock import Mock

from src.setup_environment.application.use_cases import (
    AWSCredentialsResult,
    SetupAWSCredentialsUseCase,
)
from src.setup_environment.domain.entities import AWSAccount, AWSCredentials


class TestSetupAWSCredentialsUseCase:
    """Test suite for SetupAWSCredentialsUseCase."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_sso_service = Mock()
        self.mock_config_service = Mock()
        self.use_case = SetupAWSCredentialsUseCase(
            sso_service=self.mock_sso_service,
            config_service=self.mock_config_service,
        )

    def test_find_account_by_name(self):
        """Test finding account by name."""
        accounts = [
            AWSAccount(
                name="production",
                account_id="123456789012",
                email="test@example.com",
            ),
            AWSAccount(
                name="development",
                account_id="234567890123",
                email="dev@example.com",
            ),
        ]

        result = self.use_case._find_account(accounts, "development")
        assert result.name == "development"
        assert result.account_id == "234567890123"

    def test_find_account_not_found(self):
        """Test finding account that doesn't exist."""
        accounts = [
            AWSAccount(
                name="production",
                account_id="123456789012",
                email="test@example.com",
            ),
        ]

        result = self.use_case._find_account(accounts, "nonexistent")
        assert result is None

    def test_find_account_case_insensitive(self):
        """Test finding account with case-insensitive match."""
        accounts = [
            AWSAccount(
                name="Production",
                account_id="123456789012",
                email="test@example.com",
            ),
        ]

        result = self.use_case._find_account(accounts, "production")
        assert result.name == "Production"

    def test_aws_credentials_result_creation(self):
        """Test AWSCredentialsResult creation and methods."""
        credentials = AWSCredentials(
            access_key_id="ASIAEXAMPLE123456789",
            secret_access_key="test-secret-key",
            session_token="test-session-token",
            expiration=datetime.now() + timedelta(hours=12),
            region="eu-west-2",
        )

        account = AWSAccount(
            name="production",
            account_id="123456789012",
            email="test@example.com",
        )

        result = AWSCredentialsResult(
            success=True,
            credentials=credentials,
            account=account,
            env_vars="export AWS_ACCESS_KEY_ID=...",
        )

        assert result.success is True
        assert result.is_successful() is True
        assert result.credentials == credentials
        assert result.account == account

    def test_aws_credentials_result_failure(self):
        """Test AWSCredentialsResult for failure case."""
        result = AWSCredentialsResult(
            success=False,
            error_message="Something went wrong",
        )

        assert result.success is False
        assert result.is_successful() is False
        assert result.credentials is None
        assert result.error_message == "Something went wrong"
