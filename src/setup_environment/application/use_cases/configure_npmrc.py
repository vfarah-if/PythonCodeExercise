"""Use case for configuring npmrc settings."""

from dataclasses import dataclass
from enum import Enum

from src.setup_environment.application.interfaces import NPMRCService
from src.setup_environment.domain.entities import NPMRCConfiguration
from src.setup_environment.domain.value_objects import PersonalAccessToken


class ConfigurationStatus(Enum):
    """Status of npmrc configuration."""

    CREATED = "created"
    ALREADY_EXISTS = "already_exists"
    UPDATED = "updated"


@dataclass
class ConfigureResult:
    """Result of npmrc configuration."""

    status: ConfigurationStatus
    config: NPMRCConfiguration | None = None
    message: str = ""


class ConfigureNPMRCUseCase:
    """Use case for configuring npmrc settings."""

    def __init__(self, npmrc_service: NPMRCService):
        """Initialise with an npmrc service."""
        self._npmrc_service = npmrc_service

    def execute(
        self,
        token: PersonalAccessToken | None = None,
        organisation: str = "@webuild-ai",
        registry_url: str = "https://npm.pkg.github.com",
    ) -> ConfigureResult:
        """Configure npmrc settings."""
        # Check if configuration already exists with token
        if (
            self._npmrc_service.config_exists()
            and self._npmrc_service.has_github_token()
        ):
            return ConfigureResult(
                status=ConfigurationStatus.ALREADY_EXISTS,
                message="npmrc configuration already exists with GitHub token",
            )

        # Get token if not provided
        if token is None:
            token = self._npmrc_service.prompt_for_token()

        # Create configuration
        config = NPMRCConfiguration(
            token=token,
            organisation=organisation,
            registry_url=registry_url,
        )

        # Determine status
        status = (
            ConfigurationStatus.UPDATED
            if self._npmrc_service.config_exists()
            else ConfigurationStatus.CREATED
        )

        # Write configuration
        self._npmrc_service.write_config(config)

        return ConfigureResult(
            status=status,
            config=config,
            message=f"npmrc configuration {status.value} at {self._npmrc_service.get_config_path()}",
        )
