"""Use case for configuring NPM settings."""

from dataclasses import dataclass
from enum import Enum

from src.setup_environment.application.interfaces import NPMService
from src.setup_environment.domain.entities import NPMConfiguration
from src.setup_environment.domain.value_objects import PersonalAccessToken


class ConfigurationStatus(Enum):
    """Status of NPM configuration."""

    CREATED = "created"
    ALREADY_EXISTS = "already_exists"
    UPDATED = "updated"


@dataclass
class ConfigureResult:
    """Result of NPM configuration."""

    status: ConfigurationStatus
    config: NPMConfiguration | None = None
    message: str = ""


class ConfigureNPMUseCase:
    """Use case for configuring NPM settings."""

    def __init__(self, npm_service: NPMService):
        """Initialise with an NPM service."""
        self._npm_service = npm_service

    def execute(
        self,
        token: PersonalAccessToken | None = None,
        organisation: str = "@webuild-ai",
        registry_url: str = "https://npm.pkg.github.com",
    ) -> ConfigureResult:
        """Configure NPM settings."""
        # Check if configuration already exists with token
        if self._npm_service.config_exists() and self._npm_service.has_github_token():
            return ConfigureResult(
                status=ConfigurationStatus.ALREADY_EXISTS,
                message="NPM configuration already exists with GitHub token",
            )

        # Get token if not provided
        if token is None:
            token = self._npm_service.prompt_for_token()

        # Create configuration
        config = NPMConfiguration(
            token=token,
            organisation=organisation,
            registry_url=registry_url,
        )

        # Determine status
        status = (
            ConfigurationStatus.UPDATED
            if self._npm_service.config_exists()
            else ConfigurationStatus.CREATED
        )

        # Write configuration
        self._npm_service.write_config(config)

        return ConfigureResult(
            status=status,
            config=config,
            message=f"NPM configuration {status.value} at {self._npm_service.get_config_path()}",
        )
