"""Interface for software installation service."""

from abc import ABC, abstractmethod
from pathlib import Path

from src.setup_environment.domain.entities.software import Software


class SoftwareService(ABC):
    """Abstract base class for software installation services."""

    @abstractmethod
    def is_installed(self, software: Software) -> bool:
        """Check if software is installed.

        Args:
            software: Software entity to check

        Returns:
            True if software is installed, False otherwise
        """
        pass

    @abstractmethod
    def install(self, software: Software, dry_run: bool = False) -> tuple[bool, str]:
        """Install software.

        Args:
            software: Software entity to install
            dry_run: If True, only simulate installation

        Returns:
            Tuple of (success, message)
        """
        pass

    @abstractmethod
    def load_software_config(self, config_path: Path | None = None) -> list[Software]:
        """Load software configuration from file.

        Args:
            config_path: Path to configuration file, or None for default

        Returns:
            List of Software entities
        """
        pass

    @abstractmethod
    def is_package_manager_installed(self) -> bool:
        """Check if the package manager (e.g., Homebrew) is installed.

        Returns:
            True if package manager is available
        """
        pass

    @abstractmethod
    def install_package_manager(self, dry_run: bool = False) -> tuple[bool, str]:
        """Install the package manager if not present.

        Args:
            dry_run: If True, only simulate installation

        Returns:
            Tuple of (success, message)
        """
        pass
