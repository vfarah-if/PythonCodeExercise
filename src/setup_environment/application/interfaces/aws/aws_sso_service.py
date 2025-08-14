"""Interface for AWS SSO service."""

from abc import ABC, abstractmethod

from src.setup_environment.domain.entities import AWSAccount, AWSCredentials
from src.setup_environment.domain.value_objects import AWSSession, SSOConfig


class AWSSSOService(ABC):
    """Abstract interface for AWS SSO service.

    This interface defines the contract for services that interact
    with AWS SSO to obtain temporary credentials.
    """

    @abstractmethod
    def authenticate(self, config: SSOConfig) -> AWSSession:
        """Authenticate with AWS SSO and obtain a session token.

        Args:
            config: SSO configuration

        Returns:
            AWS session with access token

        Raises:
            RuntimeError: If authentication fails
        """
        pass

    @abstractmethod
    def get_credentials(
        self,
        session: AWSSession,
        account: AWSAccount,
    ) -> AWSCredentials:
        """Get temporary AWS credentials for a specific account.

        Args:
            session: Authenticated SSO session
            account: AWS account to access

        Returns:
            Temporary AWS credentials

        Raises:
            RuntimeError: If credential retrieval fails
            ValueError: If session is expired
        """
        pass

    @abstractmethod
    def list_accounts(self, session: AWSSession) -> list[AWSAccount]:
        """List all available AWS accounts for the authenticated user.

        Args:
            session: Authenticated SSO session

        Returns:
            List of available AWS accounts

        Raises:
            RuntimeError: If account listing fails
            ValueError: If session is expired
        """
        pass

    @abstractmethod
    def refresh_session(self, config: SSOConfig) -> AWSSession:
        """Refresh an SSO session to get a new access token.

        Args:
            config: SSO configuration

        Returns:
            New AWS session with fresh access token

        Raises:
            RuntimeError: If refresh fails
        """
        pass

    @abstractmethod
    def validate_credentials(self, credentials: AWSCredentials) -> bool:
        """Validate that AWS credentials are working.

        Args:
            credentials: AWS credentials to validate

        Returns:
            True if credentials are valid and working
        """
        pass
