"""Interface for Node.js and NVM installation service."""

from abc import ABC, abstractmethod


class NodeService(ABC):
    """Abstract base class for Node.js installation services."""

    @abstractmethod
    def is_nvm_installed(self) -> bool:
        """Check if NVM is installed.

        Returns:
            True if NVM is installed, False otherwise
        """
        pass

    @abstractmethod
    def install_nvm(self, dry_run: bool = False) -> tuple[bool, str]:
        """Install NVM using the official installation script.

        Args:
            dry_run: If True, only simulate installation

        Returns:
            Tuple of (success, message)
        """
        pass

    @abstractmethod
    def install_latest_node(self, dry_run: bool = False) -> tuple[bool, str]:
        """Install the latest LTS version of Node.js.

        Args:
            dry_run: If True, only simulate installation

        Returns:
            Tuple of (success, message)
        """
        pass

    @abstractmethod
    def get_node_version(self) -> str:
        """Get currently active Node.js version.

        Returns:
            Node.js version string or 'unknown' if not available
        """
        pass

    @abstractmethod
    def setup_node_environment(self, dry_run: bool = False) -> tuple[bool, str]:
        """Set up complete Node.js environment (NVM + latest Node).

        Args:
            dry_run: If True, only simulate installation

        Returns:
            Tuple of (success, message)
        """
        pass
