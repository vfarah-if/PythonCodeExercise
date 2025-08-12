"""Unit tests for SSOConfig value object."""

import pytest

from src.setup_environment.domain.value_objects import SSOConfig


class TestSSOConfig:
    """Test suite for SSOConfig value object."""

    def test_create_sso_config_with_valid_data(self):
        """Test creating SSO config with valid data."""
        config = SSOConfig(
            sso_start_url="https://example.awsapps.com/start/#",
            sso_region="eu-west-2",
            sso_account_id="123456789012",
        )

        assert config.sso_start_url == "https://example.awsapps.com/start/#"
        assert config.sso_region == "eu-west-2"
        assert config.sso_account_id == "123456789012"

    def test_create_sso_config_with_defaults(self):
        """Test creating SSO config with default values."""
        config = SSOConfig(
            sso_start_url="https://example.awsapps.com/start/#",
        )

        assert config.sso_region == "eu-west-2"
        assert config.sso_account_id is None

    def test_equality(self):
        """Test equality comparison of SSO configs."""
        config1 = SSOConfig(
            sso_start_url="https://example.awsapps.com/start/#",
            sso_region="eu-west-2",
            sso_account_id="123456789012",
        )
        config2 = SSOConfig(
            sso_start_url="https://example.awsapps.com/start/#",
            sso_region="eu-west-2",
            sso_account_id="123456789012",
        )

        assert config1 == config2

    def test_inequality(self):
        """Test inequality comparison of SSO configs."""
        config1 = SSOConfig(
            sso_start_url="https://example.awsapps.com/start/#",
            sso_region="eu-west-2",
        )
        config2 = SSOConfig(
            sso_start_url="https://different.awsapps.com/start/#",
            sso_region="eu-west-2",
        )

        assert config1 != config2

    def test_hash_equality(self):
        """Test hash equality for configs with same values."""
        config1 = SSOConfig(
            sso_start_url="https://example.awsapps.com/start/#",
            sso_region="eu-west-2",
        )
        config2 = SSOConfig(
            sso_start_url="https://example.awsapps.com/start/#",
            sso_region="eu-west-2",
        )

        assert hash(config1) == hash(config2)

    def test_to_dict(self):
        """Test converting SSO config to dictionary."""
        config = SSOConfig(
            sso_start_url="https://example.awsapps.com/start/#",
            sso_region="us-east-1",
            sso_account_id="123456789012",
        )

        expected = {
            "sso_start_url": "https://example.awsapps.com/start/#",
            "sso_region": "us-east-1",
            "sso_account_id": "123456789012",
        }
        assert config.to_dict() == expected

    def test_to_dict_with_none_account_id(self):
        """Test converting SSO config to dictionary with None account_id."""
        config = SSOConfig(
            sso_start_url="https://example.awsapps.com/start/#",
            sso_region="us-east-1",
        )

        expected = {
            "sso_start_url": "https://example.awsapps.com/start/#",
            "sso_region": "us-east-1",
        }
        assert config.to_dict() == expected

    def test_from_env(self):
        """Test creating SSO config from dictionary."""
        env_data = {
            "AWS_SSO_START_URL": "https://example.awsapps.com/start/#",
            "AWS_SSO_REGION": "us-east-1",
            "AWS_SSO_ACCOUNT_ID": "123456789012",
        }

        config = SSOConfig.from_env(env_data)

        assert config.sso_start_url == "https://example.awsapps.com/start/#"
        assert config.sso_region == "us-east-1"
        assert config.sso_account_id == "123456789012"

    def test_from_env_with_missing_optional_fields(self):
        """Test creating SSO config from dictionary with missing optional fields."""
        env_data = {
            "AWS_SSO_START_URL": "https://example.awsapps.com/start/#",
        }

        config = SSOConfig.from_env(env_data)

        assert config.sso_start_url == "https://example.awsapps.com/start/#"
        assert config.sso_region == "eu-west-2"
        assert config.sso_account_id is None

    def test_validation_empty_start_url(self):
        """Test validation fails for empty start URL."""
        with pytest.raises(ValueError, match="SSO start URL cannot be empty"):
            SSOConfig(sso_start_url="")

    def test_validation_whitespace_start_url(self):
        """Test validation fails for whitespace-only start URL."""
        with pytest.raises(ValueError, match="SSO start URL cannot be empty"):
            SSOConfig(sso_start_url="   ")

    def test_validation_invalid_start_url_format(self):
        """Test validation fails for invalid start URL format."""
        with pytest.raises(ValueError, match="Invalid SSO URL"):
            SSOConfig(sso_start_url="not-a-url")

    def test_validation_empty_region(self):
        """Test validation fails for empty region."""
        with pytest.raises(ValueError, match="SSO region cannot be empty"):
            SSOConfig(
                sso_start_url="https://example.awsapps.com/start/#",
                sso_region="",
            )

    def test_validation_invalid_account_id(self):
        """Test validation fails for invalid account ID."""
        with pytest.raises(ValueError, match="Invalid AWS account ID"):
            SSOConfig(
                sso_start_url="https://example.awsapps.com/start/#",
                sso_account_id="invalid",
            )

    def test_validation_account_id_wrong_length(self):
        """Test validation fails for account ID with wrong length."""
        with pytest.raises(ValueError, match="Invalid AWS account ID"):
            SSOConfig(
                sso_start_url="https://example.awsapps.com/start/#",
                sso_account_id="12345",
            )

    def test_repr_representation(self):
        """Test repr representation of SSO config."""
        config = SSOConfig(
            sso_start_url="https://example.awsapps.com/start/#",
            sso_region="us-east-1",
            sso_account_id="123456789012",
        )

        expected = (
            "SSOConfig(sso_start_url='https://example.awsapps.com/start/#', "
            "sso_region='us-east-1', sso_account_id='123456789012')"
        )
        assert repr(config) == expected

    def test_str_representation(self):
        """Test string representation of SSO config."""
        config = SSOConfig(
            sso_start_url="https://example.awsapps.com/start/#",
            sso_region="us-east-1",
        )

        result = str(config)
        assert "SSO" in result
        assert "https://example.awsapps.com/start/#" in result
        assert "us-east-1" in result
