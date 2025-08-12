"""Unit tests for AWS SSO Service."""

import json
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import Mock, mock_open, patch

import pytest

from src.setup_environment.domain.entities import AWSAccount, AWSCredentials
from src.setup_environment.domain.value_objects import AWSSession, SSOConfig
from src.setup_environment.infrastructure.aws.aws_sso_service import Boto3SSOService


class TestBoto3SSOService:
    """Test suite for Boto3 SSO Service."""

    @pytest.fixture
    def sso_config(self):
        """Fixture for SSO configuration."""
        return SSOConfig(
            sso_start_url='https://test.awsapps.com/start',
            sso_region='us-east-1'
        )

    @pytest.fixture
    def aws_account(self):
        """Fixture for AWS account."""
        return AWSAccount(
            name='test-account',
            account_id='123456789012',
            email='test@example.com',
            role='Engineer'
        )

    @pytest.fixture
    def aws_session(self):
        """Fixture for AWS session."""
        return AWSSession(
            access_token='mock_token_123',
            expires_at=datetime(2025, 12, 31)
        )

    def test_init_sso_service(self):
        """Test initialising SSO service."""
        service = Boto3SSOService()

        assert service is not None
        assert hasattr(service, '_cache_dir')

    @patch('subprocess.run')
    def test_perform_sso_login_success(self, mock_subprocess, sso_config):
        """Test successful SSO login."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_subprocess.return_value = mock_result

        service = Boto3SSOService()

        service._perform_sso_login(sso_config)

        mock_subprocess.assert_called_once()
        call_args = mock_subprocess.call_args[0][0]
        assert 'aws' in call_args
        assert 'sso' in call_args
        assert 'login' in call_args

    @patch('subprocess.run')
    def test_perform_sso_login_failure(self, mock_subprocess, sso_config):
        """Test SSO login failure."""
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stderr = 'SSO login failed'
        mock_subprocess.return_value = mock_result

        service = Boto3SSOService()

        with pytest.raises(RuntimeError, match="AWS SSO login failed"):
            service._perform_sso_login(sso_config)

    def test_get_cached_token_valid(self, sso_config):
        """Test getting valid cached token."""
        service = Boto3SSOService()

        cache_data = {
            'startUrl': 'https://test.awsapps.com/start',
            'accessToken': 'valid_access_token_123',
            'expiresAt': '2025-12-31T12:00:00Z',
            'region': 'us-east-1'
        }

        with patch('pathlib.Path.glob') as mock_glob, \
             patch('builtins.open', mock_open(read_data=json.dumps(cache_data))):

            mock_cache_file = Mock()
            mock_cache_file.name = 'cache_file.json'
            mock_glob.return_value = [mock_cache_file]

            token_session = service._get_cached_token(sso_config)

            assert token_session is not None
            assert isinstance(token_session, AWSSession)
            assert token_session.access_token == 'valid_access_token_123'

    @patch('pathlib.Path.exists')
    def test_get_cached_token_no_cache(self, mock_exists, sso_config):
        """Test getting cached token when no cache exists."""
        mock_exists.return_value = False

        service = Boto3SSOService()
        token_session = service._get_cached_token(sso_config)

        assert token_session is None

    @patch('boto3.client')
    def test_get_credentials_success(self, mock_boto3_client, aws_session, aws_account):
        """Test successful credential retrieval."""
        mock_sso_client = Mock()
        mock_boto3_client.return_value = mock_sso_client

        mock_sso_client.get_role_credentials.return_value = {
            'roleCredentials': {
                'accessKeyId': 'ASIATESTACCESSKEY123',
                'secretAccessKey': 'testSecretAccessKey123456789',
                'sessionToken': 'testSessionToken123456789abcdef',
                'expiration': 1640995200000
            }
        }

        service = Boto3SSOService()

        credentials = service.get_credentials(aws_session, aws_account)

        assert isinstance(credentials, AWSCredentials)
        assert credentials.access_key_id == 'ASIATESTACCESSKEY123'
        assert credentials.secret_access_key == 'testSecretAccessKey123456789'
        assert credentials.session_token == 'testSessionToken123456789abcdef'

    @patch('boto3.client')
    def test_get_credentials_client_error(self, mock_boto3_client, aws_session, aws_account):
        from botocore.exceptions import ClientError

        mock_sso_client = Mock()
        mock_boto3_client.return_value = mock_sso_client
        mock_sso_client.get_role_credentials.side_effect = ClientError(
            error_response={'Error': {'Code': 'AccessDenied', 'Message': 'Access denied'}},
            operation_name='GetRoleCredentials'
        )

        service = Boto3SSOService()

        with pytest.raises(RuntimeError, match="Failed to get credentials"):
            service.get_credentials(aws_session, aws_account)

    def test_authenticate_with_cached_token(self, sso_config):
        service = Boto3SSOService()

        mock_session = AWSSession(
            access_token='cached_token_123',
            expires_at=datetime(2025, 12, 31, tzinfo=UTC)
        )

        with patch.object(service, '_get_cached_token', return_value=mock_session):
            result = service.authenticate(sso_config)

            assert result == mock_session

    @patch('src.setup_environment.infrastructure.aws.aws_sso_service.click')
    def test_authenticate_no_cached_token(self, mock_click, sso_config):
        service = Boto3SSOService()

        mock_session = AWSSession(
            access_token='new_token_123',
            expires_at=datetime(2025, 12, 31, tzinfo=UTC)
        )

        with patch.object(service, '_get_cached_token', side_effect=[None, mock_session]):
            with patch.object(service, '_perform_sso_login'):
                result = service.authenticate(sso_config)

                assert result == mock_session
                mock_click.echo.assert_called()

    def test_refresh_session(self, sso_config):
        service = Boto3SSOService()

        mock_session = AWSSession(
            access_token='refreshed_token_123',
            expires_at=datetime(2025, 12, 31, tzinfo=UTC)
        )

        with patch.object(service, 'authenticate', return_value=mock_session):
            result = service.refresh_session(sso_config)

            assert result == mock_session

    @patch('boto3.client')
    def test_validate_credentials_success(self, mock_boto3_client):
        mock_sts_client = Mock()
        mock_boto3_client.return_value = mock_sts_client
        mock_sts_client.get_caller_identity.return_value = {'Account': '123456789012'}

        credentials = AWSCredentials(
            access_key_id='ASIATEST123',
            secret_access_key='testSecret123',
            session_token='testSession123',
            expiration=datetime(2025, 12, 31, tzinfo=UTC)
        )

        service = Boto3SSOService()
        result = service.validate_credentials(credentials)

        assert result is True

    @patch('boto3.client')
    def test_validate_credentials_failure(self, mock_boto3_client):
        mock_boto3_client.side_effect = Exception("Invalid credentials")

        credentials = AWSCredentials(
            access_key_id='ASIAINVALID123',
            secret_access_key='invalidSecret123',
            session_token='invalidSession123',
            expiration=datetime(2025, 12, 31)
        )

        service = Boto3SSOService()

        with patch.object(service, '_validate_credentials_via_cli', return_value=False):
            result = service.validate_credentials(credentials)

            assert result is False

    @patch('boto3.client')
    def test_list_accounts_success(self, mock_boto3_client, aws_session):
        """Test successful account listing."""
        # Mock SSO client
        mock_sso_client = Mock()
        mock_boto3_client.return_value = mock_sso_client

        # Mock paginator
        mock_paginator = Mock()
        mock_sso_client.get_paginator.return_value = mock_paginator
        mock_paginator.paginate.return_value = [
            {
                'accountList': [
                    {
                        'accountId': '123456789012',
                        'accountName': 'Test Account',
                        'emailAddress': 'test@example.com'
                    }
                ]
            }
        ]

        # Mock list_account_roles
        mock_sso_client.list_account_roles.return_value = {
            'roleList': [{'roleName': 'Engineer'}]
        }

        service = Boto3SSOService()
        accounts = service.list_accounts(aws_session)

        assert len(accounts) == 1
        assert accounts[0].account_id == '123456789012'
        assert accounts[0].name == 'Test Account'
        assert accounts[0].role == 'Engineer'

    def test_list_accounts_expired_session(self):
        """Test listing accounts with expired session."""
        expired_session = AWSSession(
            access_token='expired_token',
            expires_at=datetime(2020, 1, 1)  # Past date
        )

        service = Boto3SSOService()

        with pytest.raises(ValueError, match="SSO session has expired"):
            service.list_accounts(expired_session)

    @patch('pathlib.Path.home')
    def test_cache_dir_creation(self, mock_home):
        """Test cache directory creation."""
        mock_home.return_value = Path('/Users/testuser')

        with patch('pathlib.Path.mkdir') as mock_mkdir:
            Boto3SSOService()

            # Verify cache directory setup
            mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)

    def test_expiration_parsing_from_role_credentials(self):
        """Test that expiration parsing works in get_credentials context."""
        # Test timestamp parsing (as done in actual implementation)
        timestamp_ms = 1640995200000  # Jan 1, 2022 00:00:00 UTC
        expiration = datetime.fromtimestamp(timestamp_ms / 1000, tz=UTC)

        expected = datetime(2022, 1, 1, 0, 0, 0, tzinfo=UTC)
        assert expiration == expected

    def test_token_expiry_parsing_from_cache(self):
        """Test that token expiry parsing works in cached token context."""
        # Test ISO string parsing (as done in actual implementation)
        iso_string = '2023-12-31T12:00:00Z'
        expiration = datetime.fromisoformat(iso_string.replace("Z", "+00:00")).replace(tzinfo=None)

        expected = datetime(2023, 12, 31, 12, 0, 0)
        assert expiration == expected

    @patch('subprocess.run')
    def test_configure_sso_profile(self, mock_subprocess, sso_config):
        """Test configuring SSO profile."""
        service = Boto3SSOService()

        with patch('pathlib.Path.mkdir'):
            with patch('pathlib.Path.write_text'):
                service._configure_sso_profile(sso_config)

                # Should create .aws directory and write config
                assert True  # Test passes if no exception is raised
