"""npmrc service interface."""

from abc import ABC, abstractmethod
from pathlib import Path

from src.setup_environment.domain.entities import NPMRCConfiguration
from src.setup_environment.domain.value_objects import PersonalAccessToken


class NPMRCService(ABC):
    """Interface for npmrc configuration operations."""

    @abstractmethod
    def config_exists(self) -> bool:
        """Check if npmrc configuration exists in the user's home directory."""
        pass

    @abstractmethod
    def has_github_token(self) -> bool:
        """Check if the npmrc configuration has a GitHub token configured."""
        pass

    @abstractmethod
    def write_config(self, config: NPMRCConfiguration) -> None:
        """Write npmrc configuration to the user's home directory."""
        pass

    @abstractmethod
    def get_config_path(self) -> Path:
        """Get the path to the npmrc configuration file."""
        pass

    @abstractmethod
    def prompt_for_token(self) -> PersonalAccessToken:
        """Prompt the user to create and enter a GitHub Personal Access Token."""
        pass
