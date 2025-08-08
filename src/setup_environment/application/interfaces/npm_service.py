"""NPM service interface."""

from abc import ABC, abstractmethod
from pathlib import Path

from src.setup_environment.domain.entities import NPMConfiguration
from src.setup_environment.domain.value_objects import PersonalAccessToken


class NPMService(ABC):
    """Interface for NPM configuration operations."""

    @abstractmethod
    def config_exists(self) -> bool:
        """Check if NPM configuration exists in the user's home directory."""
        pass

    @abstractmethod
    def has_github_token(self) -> bool:
        """Check if the NPM configuration has a GitHub token configured."""
        pass

    @abstractmethod
    def write_config(self, config: NPMConfiguration) -> None:
        """Write NPM configuration to the user's home directory."""
        pass

    @abstractmethod
    def get_config_path(self) -> Path:
        """Get the path to the NPM configuration file."""
        pass

    @abstractmethod
    def prompt_for_token(self) -> PersonalAccessToken:
        """Prompt the user to create and enter a GitHub Personal Access Token."""
        pass
