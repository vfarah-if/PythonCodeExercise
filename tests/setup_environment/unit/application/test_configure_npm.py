"""Unit tests for ConfigureNPMUseCase."""

from pathlib import Path
from unittest.mock import Mock

import pytest

from src.setup_environment.application.interfaces import NPMService
from src.setup_environment.application.use_cases import ConfigureNPMUseCase
from src.setup_environment.application.use_cases.configure_npm import (
    ConfigurationStatus,
    ConfigureResult,
)
from src.setup_environment.domain.entities import NPMConfiguration
from src.setup_environment.domain.value_objects import PersonalAccessToken


class TestConfigureResult:
    """Test suite for ConfigureResult class."""

    def test_configure_result_creation(self):
        """Test creating ConfigureResult instances."""
        token = PersonalAccessToken("ghp_" + "a" * 36)
        config = NPMConfiguration(token=token)

        result = ConfigureResult(
            status=ConfigurationStatus.CREATED,
            config=config,
            message="Configuration created",
        )

        assert result.status == ConfigurationStatus.CREATED
        assert result.config == config
        assert result.message == "Configuration created"


class TestConfigureNPMUseCase:
    """Test suite for ConfigureNPMUseCase."""

    @pytest.fixture
    def mock_npm_service(self):
        """Create a mock NPM service."""
        return Mock(spec=NPMService)

    @pytest.fixture
    def valid_token(self):
        """Create a valid personal access token."""
        return PersonalAccessToken("ghp_" + "a" * 36)

    def test_execute_when_config_already_exists_with_token(
        self, mock_npm_service, valid_token
    ):
        """Test execution when config already exists with a GitHub token."""
        mock_npm_service.config_exists.return_value = True
        mock_npm_service.has_github_token.return_value = True

        use_case = ConfigureNPMUseCase(mock_npm_service)
        result = use_case.execute(token=valid_token)

        assert result.status == ConfigurationStatus.ALREADY_EXISTS
        assert result.config is None
        assert "already exists" in result.message
        # Should not write config if it already exists with token
        mock_npm_service.write_config.assert_not_called()

    def test_execute_creates_new_config_with_provided_token(
        self, mock_npm_service, valid_token
    ):
        """Test creating new config with provided token."""
        mock_npm_service.config_exists.return_value = False
        mock_npm_service.get_config_path.return_value = Path("/home/user/.npmrc")

        use_case = ConfigureNPMUseCase(mock_npm_service)
        result = use_case.execute(token=valid_token)

        assert result.status == ConfigurationStatus.CREATED
        assert result.config is not None
        assert result.config.token == valid_token
        assert result.config.organisation == "@webuild-ai"
        assert "/home/user/.npmrc" in result.message

        # Verify write_config was called with correct config
        mock_npm_service.write_config.assert_called_once()
        written_config = mock_npm_service.write_config.call_args[0][0]
        assert written_config.token == valid_token

    def test_execute_updates_existing_config_without_token(
        self, mock_npm_service, valid_token
    ):
        """Test updating existing config that doesn't have a token."""
        mock_npm_service.config_exists.return_value = True
        mock_npm_service.has_github_token.return_value = False
        mock_npm_service.get_config_path.return_value = Path("/home/user/.npmrc")

        use_case = ConfigureNPMUseCase(mock_npm_service)
        result = use_case.execute(token=valid_token)

        assert result.status == ConfigurationStatus.UPDATED
        assert result.config is not None
        assert result.config.token == valid_token
        assert "updated" in result.message
        mock_npm_service.write_config.assert_called_once()

    def test_execute_prompts_for_token_when_not_provided(self, mock_npm_service):
        """Test prompting for token when not provided."""
        prompted_token = PersonalAccessToken("ghp_" + "b" * 36)
        mock_npm_service.config_exists.return_value = False
        mock_npm_service.prompt_for_token.return_value = prompted_token
        mock_npm_service.get_config_path.return_value = Path("/home/user/.npmrc")

        use_case = ConfigureNPMUseCase(mock_npm_service)
        result = use_case.execute()  # No token provided

        assert result.status == ConfigurationStatus.CREATED
        assert result.config is not None
        assert result.config.token == prompted_token
        mock_npm_service.prompt_for_token.assert_called_once()
        mock_npm_service.write_config.assert_called_once()

    def test_execute_with_custom_organisation_and_registry(
        self, mock_npm_service, valid_token
    ):
        """Test execution with custom organisation and registry."""
        mock_npm_service.config_exists.return_value = False
        mock_npm_service.get_config_path.return_value = Path("/home/user/.npmrc")

        use_case = ConfigureNPMUseCase(mock_npm_service)
        result = use_case.execute(
            token=valid_token,
            organisation="@custom-org",
            registry_url="https://custom.registry.com",
        )

        assert result.status == ConfigurationStatus.CREATED
        assert result.config is not None
        assert result.config.organisation == "@custom-org"
        assert result.config.registry_url == "https://custom.registry.com"

        # Verify the written config has custom values
        written_config = mock_npm_service.write_config.call_args[0][0]
        assert written_config.organisation == "@custom-org"
        assert written_config.registry_url == "https://custom.registry.com"

    def test_execute_does_not_prompt_when_config_exists_with_token(
        self, mock_npm_service
    ):
        """Test that token is not prompted when config already has one."""
        mock_npm_service.config_exists.return_value = True
        mock_npm_service.has_github_token.return_value = True

        use_case = ConfigureNPMUseCase(mock_npm_service)
        result = use_case.execute()  # No token provided

        assert result.status == ConfigurationStatus.ALREADY_EXISTS
        # Should not prompt for token if config already has one
        mock_npm_service.prompt_for_token.assert_not_called()

    def test_execute_integration_flow(self, mock_npm_service, valid_token):
        """Test the complete integration flow."""
        # Scenario: Config exists but without token
        mock_npm_service.config_exists.return_value = True
        mock_npm_service.has_github_token.return_value = False
        mock_npm_service.get_config_path.return_value = Path("/home/user/.npmrc")

        use_case = ConfigureNPMUseCase(mock_npm_service)

        # First execution: updates with provided token
        result1 = use_case.execute(token=valid_token)
        assert result1.status == ConfigurationStatus.UPDATED

        # Simulate that config now has token
        mock_npm_service.has_github_token.return_value = True

        # Second execution: should detect existing config with token
        result2 = use_case.execute(token=valid_token)
        assert result2.status == ConfigurationStatus.ALREADY_EXISTS

        # write_config should only be called once (first execution)
        assert mock_npm_service.write_config.call_count == 1
