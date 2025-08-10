"""Interface for Python and uv installation service."""

from abc import ABC, abstractmethod


class PythonEnvironmentService(ABC):
    """Abstract base class for Python environment installation services."""

    @abstractmethod
    def is_python_installed(self) -> bool:
        """Check if Python is installed.

        Returns:
            True if Python is installed, False otherwise
        """
        pass

    @abstractmethod
    def is_uv_installed(self) -> bool:
        """Check if uv package manager is installed.

        Returns:
            True if uv is installed, False otherwise
        """
        pass

    @abstractmethod
    def install_python(self, dry_run: bool = False) -> tuple[bool, str]:
        """Install Python using the configured method.

        Args:
            dry_run: If True, only simulate installation

        Returns:
            Tuple of (success, message)
        """
        pass

    @abstractmethod
    def install_uv(self, dry_run: bool = False) -> tuple[bool, str]:
        """Install uv package manager.

        Args:
            dry_run: If True, only simulate installation

        Returns:
            Tuple of (success, message)
        """
        pass

    @abstractmethod
    def setup_python_environment(self, dry_run: bool = False) -> tuple[bool, str]:
        """Set up complete Python environment (Python + uv).

        Args:
            dry_run: If True, only simulate installation

        Returns:
            Tuple of (success, message)
        """
        pass
