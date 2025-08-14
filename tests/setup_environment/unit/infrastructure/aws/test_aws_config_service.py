"""Unit tests for AWS Config Service."""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from src.setup_environment.domain.entities import AWSAccount
from src.setup_environment.domain.value_objects import SSOConfig
from src.setup_environment.infrastructure.aws.aws_config_service import (
    YamlAWSConfigService,
)


class TestYamlAWSConfigService:
    """Test suite for YAML AWS Config Service."""

    def _create_temp_yaml_file(self, data):
        """Create temporary YAML file with given data."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yaml') as temp_file:
            yaml.dump(data, temp_file)
            temp_file.flush()
            return temp_file

    def _create_accounts_data(self, include_dev=True):
        """Create test accounts data structure."""
        accounts = [
            {
                'name': 'production',
                'account_id': '123456789012',
                'email': 'prod@example.com',
                'role': 'Engineer',
                'default': True,
                'description': 'Production environment'
            }
        ]

        if include_dev:
            accounts.append({
                'name': 'development',
                'account_id': '234567890123',
                'email': 'dev@example.com',
                'role': 'Developer',
                'description': 'Development environment'
            })

        return {'accounts': accounts}

    def test_load_sso_config_from_env(self):
        """Test loading SSO config from environment variables."""
        with patch.dict(os.environ, {
            'AWS_SSO_START_URL': 'https://test.awsapps.com/start',
            'AWS_SSO_REGION': 'us-east-1'
        }):
            config_service = YamlAWSConfigService()
            config = config_service.load_sso_config()

            assert config.sso_start_url == 'https://test.awsapps.com/start'
            assert config.sso_region == 'us-east-1'

    def test_load_sso_config_from_dotenv(self):
        """Test loading SSO config from .env file."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.env') as file:
            file.write('AWS_SSO_START_URL=https://dotenv.awsapps.com/start\n')
            file.write('AWS_SSO_REGION=eu-west-1\n')
            file.flush()

            try:
                config_service = YamlAWSConfigService()
                config = config_service.load_sso_config(Path(file.name))

                assert config.sso_start_url == 'https://dotenv.awsapps.com/start'
                assert config.sso_region == 'eu-west-1'
            finally:
                os.unlink(file.name)

    def test_load_sso_config_missing_url_fails(self):
        """Test loading SSO config fails when URL is missing."""
        with patch.dict(os.environ, {}, clear=True):
            with patch('pathlib.Path.exists', return_value=False):
                config_service = YamlAWSConfigService()

                with pytest.raises(ValueError, match="AWS_SSO_START_URL not found"):
                    config_service.load_sso_config()

    def test_load_accounts_from_yaml_file(self):
        """Test loading accounts from YAML file."""
        accounts_data = self._create_accounts_data()
        file = self._create_temp_yaml_file(accounts_data)

        try:
            config_service = YamlAWSConfigService()
            accounts = config_service.load_accounts(Path(file.name))

            assert len(accounts) == 2

            prod_account = accounts[0]
            assert prod_account.name == 'production'
            assert prod_account.account_id == '123456789012'
            assert prod_account.email == 'prod@example.com'
            assert prod_account.role == 'Engineer'
            assert prod_account.is_default is True

            dev_account = accounts[1]
            assert dev_account.name == 'development'
            assert dev_account.account_id == '234567890123'
            assert dev_account.email == 'dev@example.com'
            assert dev_account.role == 'Developer'
            assert dev_account.is_default is False
        finally:
            os.unlink(file.name)

    def test_load_accounts_file_not_found(self):
        """Test loading accounts when file doesn't exist."""
        config_service = YamlAWSConfigService()

        with pytest.raises(FileNotFoundError, match="AWS accounts configuration not found"):
            config_service.load_accounts(Path('/nonexistent/path/accounts.yaml'))

    def test_load_accounts_invalid_yaml(self):
        """Test loading accounts with invalid YAML."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yaml') as file:
            file.write('invalid: yaml: content: [unclosed')
            file.flush()

            try:
                config_service = YamlAWSConfigService()

                with pytest.raises(ValueError, match="Failed to parse YAML configuration"):
                    config_service.load_accounts(Path(file.name))
            finally:
                os.unlink(file.name)

    def test_load_accounts_missing_accounts_key(self):
        """Test loading accounts with missing 'accounts' key."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yaml') as file:
            yaml.dump({'invalid': 'structure'}, file)
            file.flush()

            try:
                config_service = YamlAWSConfigService()

                with pytest.raises(ValueError, match="Invalid AWS accounts configuration"):
                    config_service.load_accounts(Path(file.name))
            finally:
                os.unlink(file.name)

    def test_save_credentials_to_file(self):
        """Test saving credentials to file."""
        config_service = YamlAWSConfigService()

        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / 'credentials.txt'
            credentials = 'export AWS_ACCESS_KEY_ID=test'

            config_service.save_credentials_to_file(credentials, file_path)

            assert file_path.exists()
            assert file_path.read_text() == credentials

    def test_load_sso_config_validates_returned_config(self):
        """Test that load_sso_config returns valid SSOConfig object."""
        with patch.dict(os.environ, {
            'AWS_SSO_START_URL': 'https://test.awsapps.com/start',
            'AWS_SSO_REGION': 'us-east-1'
        }):
            config_service = YamlAWSConfigService()
            config = config_service.load_sso_config()

            assert isinstance(config, SSOConfig)
            assert hasattr(config, 'sso_start_url')
            assert hasattr(config, 'sso_region')

    def test_load_accounts_returns_aws_account_objects(self):
        """Test that load_accounts returns proper AWSAccount objects."""
        accounts_data = {
            'accounts': [{
                'name': 'test-account',
                'account_id': '123456789012',
                'email': 'test@example.com',
                'role': 'Engineer'
            }]
        }
        file = self._create_temp_yaml_file(accounts_data)

        try:
            config_service = YamlAWSConfigService()
            accounts = config_service.load_accounts(Path(file.name))

            assert isinstance(accounts, list)
            assert len(accounts) == 1
            assert isinstance(accounts[0], AWSAccount)

            account = accounts[0]
            assert account.name == 'test-account'
            assert account.account_id == '123456789012'
            assert account.email == 'test@example.com'
            assert account.role == 'Engineer'
            assert account.is_default is False
        finally:
            os.unlink(file.name)
