"""Interface for repository configuration service."""

from abc import ABC, abstractmethod

from src.setup_environment.domain.entities import Repository


class RepositoryConfigurationService(ABC):
    """Abstract base class for repository configuration services."""

    @abstractmethod
    def load_repositories(self, config_path: str | None = None) -> list[Repository]:
        """Load repository configurations from configuration source.

        Args:
            config_path: Optional path to custom configuration file.
                        If not provided, uses default location.

        Returns:
            List of Repository entities.

        Raises:
            FileNotFoundError: If configuration file doesn't exist.
            ValueError: If configuration is invalid.
        """
        pass
