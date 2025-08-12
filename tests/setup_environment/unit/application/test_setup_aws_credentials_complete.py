"""Unit tests for Setup AWS Credentials Use Case."""

from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from src.setup_environment.application.use_cases.setup_aws_credentials import (
    AWSCredentialsResult,
    SetupAWSCredentialsUseCase,
)
from src.setup_environment.domain.entities import AWSAccount, AWSCredentials
from src.setup_environment.domain.value_objects import AWSSession, SSOConfig


class TestSetupAWSCredentialsUseCase:
    """Comprehensive test suite for Setup AWS Credentials Use Case."""

    def _setup_successful_mocks(self, mock_config_service, mock_sso_service, sso_config, accounts_list, mock_credentials, mock_session):
        """Configure mocks for successful credential retrieval."""
        mock_config_service.load_sso_config.return_value = sso_config
        mock_config_service.load_accounts.return_value = accounts_list
        mock_sso_service.authenticate.return_value = mock_session
        mock_sso_service.get_credentials.return_value = mock_credentials
        mock_sso_service.validate_credentials.return_value = True

    def _assert_successful_result(self, result, expected_account_name, mock_credentials):
        """Assert result indicates success with expected values."""
        assert result.success is True
        assert result.account.name == expected_account_name
        assert result.credentials == mock_credentials
        assert 'export AWS_ACCESS_KEY_ID=' in result.env_vars

    @pytest.fixture
    def mock_sso_service(self):
        """Mock SSO service fixture."""
        return Mock()

    @pytest.fixture
    def mock_config_service(self):
        """Mock config service fixture."""
        return Mock()

    @pytest.fixture
    def use_case(self, mock_sso_service, mock_config_service):
        return SetupAWSCredentialsUseCase(mock_sso_service, mock_config_service)

    @pytest.fixture
    def sso_config(self):
        """SSO configuration fixture."""
        return SSOConfig(
            sso_start_url='https://test.awsapps.com/start',
            sso_region='us-east-1'
        )

    @pytest.fixture
    def accounts_list(self):
        """List of AWS accounts fixture."""
        return [
            AWSAccount(
                name='production',
                account_id='123456789012',
                email='prod@example.com',
                role='Engineer',
                is_default=False
            ),
            AWSAccount(
                name='development',
                account_id='234567890123',
                email='dev@example.com',
                role='Engineer',
                is_default=True
            ),
            AWSAccount(
                name='staging',
                account_id='345678901234',
                email='staging@example.com',
                role='Engineer',
                is_default=False
            )
        ]

    @pytest.fixture
    def mock_credentials(self):
        """Mock credentials fixture."""
        return AWSCredentials(
            access_key_id='ASIAMOCKACCKEY123',
            secret_access_key='mockSecretKey123456789',
            session_token='mockSessionToken123456789abcdef',
            expiration=datetime(2024, 12, 31, 12, 0, 0),
            region='us-west-2'
        )

    @pytest.fixture
    def mock_session(self):
        """Mock AWS session fixture."""
        session = Mock(spec=AWSSession)
        session.is_expired.return_value = False
        return session

    def test_execute_with_specific_account_name(self, use_case, mock_sso_service, mock_config_service,
                                                sso_config, accounts_list, mock_credentials, mock_session):
        """Test executing use case with specific account name."""
        self._setup_successful_mocks(mock_config_service, mock_sso_service, sso_config, accounts_list, mock_credentials, mock_session)

        result = use_case.execute(account_name='development')

        self._assert_successful_result(result, 'development', mock_credentials)
        mock_config_service.load_sso_config.assert_called_once_with(None)
        mock_config_service.load_accounts.assert_called_once_with(None)
        mock_sso_service.authenticate.assert_called_once_with(sso_config)
        mock_sso_service.get_credentials.assert_called_once_with(mock_session, accounts_list[1])

    @patch('click.prompt')
    def test_execute_with_default_account(self, mock_prompt, use_case, mock_sso_service,
                                          mock_config_service, sso_config, accounts_list,
                                          mock_credentials, mock_session):
        """Test executing use case without account name (uses default)."""
        self._setup_successful_mocks(mock_config_service, mock_sso_service, sso_config, accounts_list, mock_credentials, mock_session)
        mock_config_service.get_default_account.return_value = accounts_list[1]
        mock_prompt.return_value = 2

        result = use_case.execute()

        self._assert_successful_result(result, 'development', mock_credentials)
        mock_config_service.get_default_account.assert_called_once_with(accounts_list)

    def test_execute_account_not_found(self, use_case, mock_config_service, sso_config, accounts_list):
        """Test executing use case with non-existent account name."""
        mock_config_service.load_sso_config.return_value = sso_config
        mock_config_service.load_accounts.return_value = accounts_list

        result = use_case.execute(account_name='nonexistent')

        assert result.success is False
        assert "Account 'nonexistent' not found" in result.error_message

    def test_execute_sso_service_error(self, use_case, mock_sso_service, mock_config_service,
                                       sso_config, accounts_list):
        """Test executing use case when SSO service fails."""
        mock_config_service.load_sso_config.return_value = sso_config
        mock_config_service.load_accounts.return_value = accounts_list
        mock_sso_service.authenticate.side_effect = RuntimeError("SSO authentication failed")

        result = use_case.execute(account_name='development')

        assert result.success is False
        assert "SSO authentication failed" in result.error_message

    def test_execute_config_service_sso_error(self, use_case, mock_config_service):
        """Test executing use case when config service fails to load SSO config."""
        mock_config_service.load_sso_config.side_effect = ValueError("Failed to load SSO configuration")

        result = use_case.execute()

        assert result.success is False
        assert "Failed to load SSO configuration" in result.error_message

    def test_execute_config_service_accounts_error(self, use_case, mock_config_service, sso_config):
        """Test executing use case when config service fails to load accounts."""
        mock_config_service.load_sso_config.return_value = sso_config
        mock_config_service.load_accounts.side_effect = FileNotFoundError("Failed to load accounts configuration")

        result = use_case.execute()

        assert result.success is False
        assert "Failed to load accounts configuration" in result.error_message

    def test_execute_with_empty_accounts_list(self, use_case, mock_config_service, sso_config):
        """Test executing use case with empty accounts list."""
        mock_config_service.load_sso_config.return_value = sso_config
        mock_config_service.load_accounts.return_value = []

        result = use_case.execute()

        assert result.success is False
        assert "No AWS accounts configured" in result.error_message

    @patch('click.prompt')
    def test_execute_with_custom_config_paths(self, mock_prompt, use_case, mock_sso_service,
                                              mock_config_service, sso_config, accounts_list,
                                              mock_credentials, mock_session):
        """Test executing use case with custom configuration paths."""
        # Setup mocks
        mock_config_service.load_sso_config.return_value = sso_config
        mock_config_service.load_accounts.return_value = accounts_list
        mock_config_service.get_default_account.return_value = accounts_list[0]
        mock_sso_service.authenticate.return_value = mock_session
        mock_sso_service.get_credentials.return_value = mock_credentials
        mock_sso_service.validate_credentials.return_value = True
        mock_prompt.return_value = 1

        # Custom paths
        env_file = Path("/custom/.env")
        config_file = Path("/custom/accounts.yaml")
        output_file = Path("/custom/credentials.txt")

        # Execute
        result = use_case.execute(
            env_file=env_file,
            config_file=config_file,
            output_file=output_file
        )

        # Verify
        assert result.success is True
        mock_config_service.load_sso_config.assert_called_once_with(env_file)
        mock_config_service.load_accounts.assert_called_once_with(config_file)
        mock_config_service.save_credentials_to_file.assert_called_once()

    @patch('click.prompt')
    def test_execute_with_different_export_formats(self, mock_prompt, use_case, mock_sso_service,
                                                   mock_config_service, sso_config, accounts_list,
                                                   mock_credentials, mock_session):
        """Test executing use case with different export formats."""
        # Setup mocks
        mock_config_service.load_sso_config.return_value = sso_config
        mock_config_service.load_accounts.return_value = accounts_list
        mock_config_service.get_default_account.return_value = accounts_list[0]
        mock_sso_service.authenticate.return_value = mock_session
        mock_sso_service.get_credentials.return_value = mock_credentials
        mock_sso_service.validate_credentials.return_value = True
        mock_prompt.return_value = 1

        # Test bash format
        result_bash = use_case.execute(export_format='bash')
        assert 'export AWS_ACCESS_KEY_ID=' in result_bash.env_vars
        assert result_bash.success is True

    @patch('click.prompt')
    def test_result_contains_all_required_fields(self, mock_prompt, use_case, mock_sso_service,
                                                 mock_config_service, sso_config, accounts_list,
                                                 mock_credentials, mock_session):
        """Test that result contains all required fields."""
        # Setup mocks
        mock_config_service.load_sso_config.return_value = sso_config
        mock_config_service.load_accounts.return_value = accounts_list
        mock_config_service.get_default_account.return_value = accounts_list[0]
        mock_sso_service.authenticate.return_value = mock_session
        mock_sso_service.get_credentials.return_value = mock_credentials
        mock_sso_service.validate_credentials.return_value = True
        mock_prompt.return_value = 1

        # Execute
        result = use_case.execute()

        # Verify all required fields are present
        assert hasattr(result, 'success')
        assert hasattr(result, 'credentials')
        assert hasattr(result, 'account')
        assert hasattr(result, 'env_vars')
        assert hasattr(result, 'error_message')
        assert result.is_successful() is True

        # Verify types
        assert isinstance(result.success, bool)
        assert isinstance(result.credentials, AWSCredentials)
        assert isinstance(result.account, AWSAccount)
        assert isinstance(result.env_vars, str)


class TestAWSCredentialsResult:
    """Test the AWSCredentialsResult dataclass."""

    def test_result_initialization(self):
        """Test result initialization."""
        result = AWSCredentialsResult(success=True)
        assert result.success is True
        assert result.credentials is None

    def test_is_successful_method(self):
        """Test is_successful method."""
        # Success with credentials
        credentials = AWSCredentials('ASIATEST123', 'secret', 'token', datetime.now())
        result = AWSCredentialsResult(success=True, credentials=credentials)
        assert result.is_successful() is True

        # Success without credentials
        result = AWSCredentialsResult(success=True, credentials=None)
        assert result.is_successful() is False

        # Failure
        result = AWSCredentialsResult(success=False)
        assert result.is_successful() is False
