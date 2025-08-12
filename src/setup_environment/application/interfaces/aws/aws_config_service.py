"""Interface for AWS configuration service."""

from abc import ABC, abstractmethod
from pathlib import Path

from src.setup_environment.domain.entities import AWSAccount
from src.setup_environment.domain.value_objects import SSOConfig


class AWSConfigService(ABC):
    """Abstract interface for AWS configuration service.

    This interface defines the contract for services that load
    and manage AWS configuration from various sources.
    """

    @abstractmethod
    def load_sso_config(self, env_file: Path | None = None) -> SSOConfig:
        """Load SSO configuration from environment or .env file.

        Args:
            env_file: Optional path to .env file

        Returns:
            SSO configuration

        Raises:
            ValueError: If required configuration is missing
        """
        pass

    @abstractmethod
    def load_accounts(self, config_file: Path | None = None) -> list[AWSAccount]:
        """Load AWS account definitions from configuration file.

        Args:
            config_file: Optional path to accounts YAML file

        Returns:
            List of AWS accounts

        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If config file is invalid
        """
        pass

    @abstractmethod
    def save_credentials_to_file(
        self,
        credentials: str,
        file_path: Path,
    ) -> None:
        """Save credentials to a file.

        Args:
            credentials: Credentials string to save
            file_path: Path to save file

        Raises:
            IOError: If file cannot be written
        """
        pass

    @abstractmethod
    def get_default_account(self, accounts: list[AWSAccount]) -> AWSAccount | None:
        """Get the default account from a list of accounts.

        Args:
            accounts: List of AWS accounts

        Returns:
            Default account if one exists, None otherwise
        """
        pass
